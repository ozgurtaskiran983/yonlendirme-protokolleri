import networkx as nx
import matplotlib.pyplot as plt
import heapq
import random

#Matlab tarzı ızgara görünümü için stil ayarı yapıyoruz
plt.style.use('ggplot') 

class AkilliAgSimulasyonu:
    def __init__(self):
        #NetworkX kütüphanesini kullanarak boş bir ağ grafiği oluşturuyoruz
        self.graph = nx.Graph()

    def yol_ekle(self, u, v, mesafe, trafik_yogunlugu):
        """
        mesafe: Km cinsinden uzunluk (Düşük olması iyidir)
        trafik_yogunlugu: 0.0 (Boş) - 1.0 (Kilitli) arası
        """
        #Grafiğe iki nokta arasındaki hem fiziksel mesafeyi hem de trafik verisini ekliyoruz
        self.graph.add_edge(u, v, weight=mesafe, traffic=trafik_yogunlugu)

    def klasik_dijkstra(self, baslangic, hedef):
        #Klasik dijkstra algoritması sadece fiziksel mesafeye odaklanır ve trafik yoğunluğunu tamamen görmezden gelir
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        pq = [(0, baslangic)]
        onceki = {node: None for node in self.graph.nodes}

        while pq:
            mevcut_maliyet, mevcut_dugum = heapq.heappop(pq)
            if mevcut_dugum == hedef: break
            if mevcut_maliyet > mesafeler[mevcut_dugum]: continue

            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                #Maliyet olarak sadece fiziksel mesafe (weight) alınıyor
                yeni_maliyet = mevcut_maliyet + ozellikler['weight']
                if yeni_maliyet < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_maliyet
                    onceki[komsu] = mevcut_dugum
                    heapq.heappush(pq, (yeni_maliyet, komsu))
        
        return self._yolu_kur(hedef, onceki), mesafeler[hedef]

    def modifiye_dijkstra(self, baslangic, hedef):
        #Geliştirdiğimiz algoritma mesafenin yanında trafik yoğunluğunu da bir ceza puanı olarak hesaba katar
        #Algoritmanın Formülü: Maliyet = Mesafe * (1 + (Trafik * Ceza_Katsayısı))
        
        #Trafik varsa o yolun maliyetini 5 katına kadar artırarak algoritmayı o yoldan soğutuyoruz
        CEZA_KATSAYISI = 10.0 
        
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        pq = [(0, baslangic)]
        onceki = {node: None for node in self.graph.nodes}

        while pq:
            mevcut_maliyet, mevcut_dugum = heapq.heappop(pq)
            if mevcut_dugum == hedef: break
            if mevcut_maliyet > mesafeler[mevcut_dugum]: continue

            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                mesafe = ozellikler['weight']
                trafik = ozellikler['traffic']
                
                
                #Sadece mesafeyi toplamak yerine trafik yoğunluğuna göre dinamik bir maliyet hesaplıyoruz
                efektif_maliyet = mesafe * (1 + (trafik * CEZA_KATSAYISI))
                
                yeni_maliyet = mevcut_maliyet + efektif_maliyet
                if yeni_maliyet < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_maliyet
                    onceki[komsu] = mevcut_dugum
                    heapq.heappush(pq, (yeni_maliyet, komsu))
        
        return self._yolu_kur(hedef, onceki), mesafeler[hedef]

    def _yolu_kur(self, hedef, onceki_sozlugu):
        #Bulunan en kısa rotayı hedef noktadan geriye doğru giderek oluşturuyoruz
        yol = []
        curr = hedef
        while curr is not None:
            yol.insert(0, curr)
            curr = onceki_sozlugu[curr]
        return yol

    def gorsellestir_karsilastir(self, baslangic, hedef):
        #1. ANALİZ ADIMI
        #Her iki algoritmayı da çalıştırıp buldukları yolları alıyoruz
        klasik_yol, k_maliyet = self.klasik_dijkstra(baslangic, hedef)
        modifiye_yol, m_maliyet = self.modifiye_dijkstra(baslangic, hedef)

        #2. GÖRSELLEŞTİRME AYARLARI
        #Düğümlerin ekrandaki yerini sabitliyoruz ki her çalıştığında kaymasın
        pos = nx.spring_layout(self.graph, seed=12) 
        plt.figure(figsize=(14, 8))
        
        #A. ALT YAPI VE TRAFİK GÖSTERİMİ
        edges = self.graph.edges()
        traffic_values = [self.graph[u][v]['traffic'] for u, v in edges]
        
        #Ağdaki yolları trafik durumuna göre renklendiriyoruz (Yeşil: Açık, Kırmızı: Tıkalı)
        nx.draw_networkx_edges(self.graph, pos, edge_color=traffic_values, 
                               edge_cmap=plt.cm.RdYlGn_r, width=2, alpha=0.4)
        nx.draw_networkx_nodes(self.graph, pos, node_size=700, node_color='lightgray')
        nx.draw_networkx_labels(self.graph, pos, font_weight='bold')
        
        #Bağlantıların üzerine Mesafe ve Trafik Yüzdesini yazıyoruz
        edge_labels = {
            (u, v): f"{d['weight']}km\n%{int(d['traffic']*100)}" 
            for u, v, d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)

        #B. BULUNAN YOLLARI ÇİZME
        
        #Klasik algoritmanın bulduğu yolu Mavi ve Kesikli çizgiyle gösteriyoruz
        path_edges_klasik = list(zip(klasik_yol, klasik_yol[1:]))
        nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges_klasik, 
                               edge_color='blue', width=4, style='dashed', 
                               label='Standart Dijkstra (Sadece Mesafe)')

        #Geliştirdiğimiz algoritmanın yolunu Yeşil ve Düz çizgiyle gösteriyoruz
        path_edges_modifiye = list(zip(modifiye_yol, modifiye_yol[1:]))
        
        #Çizgiler üst üste binip kaybolmasın diye yeşil çizgiyi biraz şeffaf yapıyoruz
        nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges_modifiye, 
                               edge_color='green', width=3, alpha=0.7, 
                               label='Geliştirilmiş Dijkstra (Trafik Duyarlı)')

        #C. SONUÇ BİLGİ EKRANI
        #Grafiğin sol üst köşesine hangi çizginin ne anlama geldiğini koyuyoruz
        plt.legend(loc='upper left', fontsize=11)
        
        #Analiz sonucunu özetleyen bir bilgi metni hazırlayıp sağ alt köşeye yerleştiriyoruz
        info_text = (
            f"ANALİZ SONUCU:\n"
            f"-----------------------------------\n"
            f"(Mavi) Standart Dijkstra Algortiması\n"
            f"Seçilen Rota: {klasik_yol}\n"
            f"Rota Durumu: KISA YOL ama YAVAŞ\n"
            f"-----------------------------------\n"
            f"(Yeşil) Geliştirilmiş Dijkstra Algortiması\n"
            f"Seçilen Rota: {modifiye_yol}\n"
            f"Rota Durumu: UZUN YOL ama HIZLI\n"
            f"-----------------------------------\n"
            f"SONUÇ: Geliştirilmiş Dijkstra algoritması trafiğe duyarlılığı sayesinde \n"
            f"yoğunluğu önleyerek verimi artırdı."
        )
        plt.text(0.98, 0.02, info_text, transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        plt.title(f"Standart vs Trafik Duyarlı Yönlendirme", fontsize=15)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    sim = AkilliAgSimulasyonu()
    
    #SENARYO TASARIMI
    #Algoritmaları test etmek için özel bir tuzak senaryosu kuruyoruz
    #0 noktasından 5 noktasına gitmeye çalışacağız
    
    #YOL 1: Çok kısa (2+2=4km) ama trafik felaket (%95 dolu). Klasik algoritma buraya düşecek.
    sim.yol_ekle(0, 1, mesafe=2, trafik_yogunlugu=0.95) 
    sim.yol_ekle(1, 5, mesafe=2, trafik_yogunlugu=0.95) 

    #YOL 2: Biraz daha uzun (3+3+3=9km) ama trafik çok rahat (%10 dolu). Akıllı algoritma bunu seçmeli.
    sim.yol_ekle(0, 2, mesafe=3, trafik_yogunlugu=0.10) 
    sim.yol_ekle(2, 3, mesafe=3, trafik_yogunlugu=0.10)
    sim.yol_ekle(3, 5, mesafe=3, trafik_yogunlugu=0.0)

    #YOL 3: Çok çok uzun yol (Alternatif olarak ekliyoruz)
    sim.yol_ekle(0, 4, mesafe=10, trafik_yogunlugu=0.0)
    sim.yol_ekle(4, 5, mesafe=10, trafik_yogunlugu=0.0)

    #Ağı karmaşıklaştırmak için ara bağlantılar ekliyoruz
    sim.yol_ekle(1, 2, mesafe=1, trafik_yogunlugu=0.5)
    sim.yol_ekle(3, 4, mesafe=2, trafik_yogunlugu=0.2)

    #Simülasyonu başlatıp sonucu ekrana çizdiriyoruz
    print("Simülasyon başlatılıyor...")
    sim.gorsellestir_karsilastir(0, 5)