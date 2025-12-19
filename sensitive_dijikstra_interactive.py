import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import heapq
import random
import math

#Grafiklerin daha temiz görünmesi için varsayılan stili kullanıyoruz
plt.style.use('default') 

class InteraktifAgSimulasyonu:
    def __init__(self, dugum_sayisi=50):
        #Noktaların rastgele ama coğrafi olarak mantıklı dağılması için geometrik graf kullanıyoruz
        self.graph = nx.random_geometric_graph(dugum_sayisi, radius=0.3, seed=42)
        self.pos = nx.get_node_attributes(self.graph, 'pos')
        
        for (u, v) in self.graph.edges():
            #İki nokta arasındaki kuş uçuşu mesafeyi (Öklid) hesaplayıp ağırlık olarak atıyoruz
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 100 
            self.graph.edges[u, v]['weight'] = round(dist, 1)
            
            #Gerçekçi bir simülasyon için yollara rastgele trafik yoğunluğu atıyoruz
            zar = random.random()
            if zar < 0.50: 
                #%50 ihtimalle yol açık (Yeşil)
                self.graph.edges[u, v]['traffic'] = random.uniform(0.0, 0.40)
            elif zar < 0.80:
                #%30 ihtimalle trafik orta seviyede (Turuncu)
                self.graph.edges[u, v]['traffic'] = random.uniform(0.40, 0.75)
            else:
                #%20 ihtimalle trafik kilit (Kırmızı)
                self.graph.edges[u, v]['traffic'] = random.uniform(0.75, 1.0)

    def gercek_maliyet_hesapla(self, yol):
        #Karşılaştırmanın adil olması için her iki rotanın da hem mesafesini hem de trafik cezasını hesaplıyoruz
        toplam_km = 0
        toplam_puan = 0
        CEZA_KATSAYISI = 10.0 
        
        if not yol: return 0, 0

        for i in range(len(yol)-1):
            u, v = yol[i], yol[i+1]
            data = self.graph[u][v]
            km = data['weight']
            trafik = data['traffic']
            
            toplam_km += km
            #Geliştirdiğimiz algoritmada Mesafe * (1 + Trafik Cezası) formülü ile gerçek zorluğu buluyoruz
            maliyet = km * (1 + (trafik * CEZA_KATSAYISI))
            toplam_puan += maliyet
            
        return round(toplam_km, 2), round(toplam_puan, 2)

    def klasik_dijkstra(self, baslangic, hedef):
        try:
            #Klasik algoritma sadece fiziksel mesafeye bakar, trafiği görmezden gelir
            mesafeler = {node: float('infinity') for node in self.graph.nodes}
            mesafeler[baslangic] = 0
            pq = [(0, baslangic)]
            onceki = {node: None for node in self.graph.nodes}

            while pq:
                mevcut_maliyet, mevcut_dugum = heapq.heappop(pq)
                if mevcut_dugum == hedef: break
                if mevcut_maliyet > mesafeler[mevcut_dugum]: continue

                for komsu, ozellikler in self.graph[mevcut_dugum].items():
                    yeni_maliyet = mevcut_maliyet + ozellikler['weight']
                    if yeni_maliyet < mesafeler[komsu]:
                        mesafeler[komsu] = yeni_maliyet
                        onceki[komsu] = mevcut_dugum
                        heapq.heappush(pq, (yeni_maliyet, komsu))
            return self._yolu_kur(hedef, onceki)
        except:
            return []

    def modifiye_dijkstra(self, baslangic, hedef):
        try:
            #Bizim geliştirdiğimiz algoritma: Mesafeyi trafik yoğunluğu ile çarparak sanal bir maliyet çıkarır
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
                    
                    #Dinamik Maliyet Hesabı: Yol tıkalıysa maliyeti 10 katına kadar artırıyoruz
                    efektif_maliyet = mesafe * (1 + (trafik * CEZA_KATSAYISI))
                    
                    yeni_maliyet = mevcut_maliyet + efektif_maliyet
                    if yeni_maliyet < mesafeler[komsu]:
                        mesafeler[komsu] = yeni_maliyet
                        onceki[komsu] = mevcut_dugum
                        heapq.heappush(pq, (yeni_maliyet, komsu))
            return self._yolu_kur(hedef, onceki)
        except:
            return []

    def _yolu_kur(self, hedef, onceki_sozlugu):
        #Bulunan en kısa yolu sondan başa doğru birleştirerek listeyi oluşturuyoruz
        yol = []
        curr = hedef
        while curr is not None:
            yol.insert(0, curr)
            curr = onceki_sozlugu[curr]
        return yol

#Simülasyonu başlatıyoruz ve arayüz pencerelerini ayarlıyoruz
simulation = InteraktifAgSimulasyonu(dugum_sayisi=50)
fig, ax = plt.subplots(figsize=(13, 8))
#Alt kısımda buton ve kutucuklara yer açmak için boşluk bırakıyoruz
plt.subplots_adjust(bottom=0.2) 

def haritayi_ciz(yol_klasik=None, yol_modifiye=None, sonuc_metni=""):
    ax.clear()
    
    #Kenarları trafik yoğunluğuna göre renklendiriyoruz (Yeşil-Turuncu-Kırmızı)
    edges = simulation.graph.edges()
    colors = []
    widths = []
    
    for u, v in edges:
        trafik = simulation.graph[u][v]['traffic']
        
        if trafik > 0.75:       #Çok Yoğun Trafik (Kırmızı)
            colors.append('red')      
            widths.append(2.0)
        elif trafik > 0.40:     #Orta Yoğunluk (Turuncu)
            colors.append('orange')   
            widths.append(1.5)
        else:                   #Rahat Trafik (Yeşil)
            colors.append('lightgreen') 
            widths.append(1.0)
    
    nx.draw(simulation.graph, simulation.pos, ax=ax, 
            node_color='lightgrey', node_size=300, 
            edge_color=colors, width=widths, 
            with_labels=True, font_size=8, font_weight='bold')
    
    #Ekranın karışmaması için sadece Kırmızı (%75 üzeri) yollara yüzde etiketi basıyoruz
    edge_labels = {}
    for u, v, d in simulation.graph.edges(data=True):
        if d['traffic'] > 0.75:
             edge_labels[(u, v)] = f"%{int(d['traffic']*100)}"
             
    nx.draw_networkx_edge_labels(simulation.graph, simulation.pos, ax=ax, 
                                 edge_labels=edge_labels, font_size=7, font_color='darkred', font_weight='bold')

    #Klasik Dijkstra'nın bulduğu yolu Mavi ve Kesikli çizgiyle gösteriyoruz
    if yol_klasik:
        edges_k = list(zip(yol_klasik, yol_klasik[1:]))
        nx.draw_networkx_edges(simulation.graph, simulation.pos, ax=ax, edgelist=edges_k, 
                               edge_color='blue', width=4, style='dashed', alpha=0.7, label='Dijkstra (Mesafe Duyarlı)')
        
    #Bizim Akıllı Algoritmanın bulduğu yolu Mor ve Düz çizgiyle gösteriyoruz
    if yol_modifiye:
        edges_m = list(zip(yol_modifiye, yol_modifiye[1:]))
        nx.draw_networkx_edges(simulation.graph, simulation.pos, ax=ax, edgelist=edges_m, 
                               edge_color='purple', width=3, alpha=0.9, label='Geliştirilmiş Dijkstra (Trafik Duyarlı)')

    #Sonuçları gösteren bilgi kutusunu sol üst köşeye yerleştiriyoruz
    if sonuc_metni:
        props = dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='black')
        ax.text(0.02, 0.98, sonuc_metni, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props, fontname='monospace')

    ax.set_title("50 Router'lı Akıllı Ağ Simülasyonu", fontsize=14)
    if yol_klasik or yol_modifiye: ax.legend(loc='upper right')
    plt.draw()

def hesapla(event):
    try:
        #Kullanıcının girdiği başlangıç ve bitiş noktalarını alıyoruz
        start_node = int(text_box_start.text)
        end_node = int(text_box_end.text)
        
        #Girilen noktaların haritada olup olmadığını kontrol ediyoruz
        if start_node not in simulation.graph.nodes or end_node not in simulation.graph.nodes:
            haritayi_ciz(sonuc_metni="HATA: Haritada görünen\nnumaraları giriniz.")
            return

        #Her iki algoritmayı da çalıştırıp rotaları buluyoruz
        path_k = simulation.klasik_dijkstra(start_node, end_node)
        path_m = simulation.modifiye_dijkstra(start_node, end_node)
        
        if not path_k:
            haritayi_ciz(sonuc_metni="HATA: Yol bulunamadı!")
            return

        #Sonuçları karşılaştırmak için gerçek maliyetleri hesaplıyoruz
        km_k, puan_k = simulation.gercek_maliyet_hesapla(path_k)
        km_m, puan_m = simulation.gercek_maliyet_hesapla(path_m)
        fark = puan_k - puan_m

        #Ekrana yazılacak rapor metnini hazırlıyoruz
        sonuc_metni = (
            f"--- {start_node} -> {end_node} ANALİZİ ---\n\n"
            f" Dijkstra Algoritması\n"
            f"• Mesafe:   {km_k} km\n"
            f"• SÜRE/PUAN: {puan_k}\n\n"
            f" Geliştirilmiş Dijkstra Algoritması\n"
            f"• Mesafe:   {km_m} km\n"
            f"• SÜRE/PUAN: {puan_m}\n\n"
            f"SONUÇ: {round(fark, 2)} puan kâr!"
        )

        haritayi_ciz(path_k, path_m, sonuc_metni)
        
    except ValueError:
        print("Lütfen sayı girin!")

#Arayüz elemanlarını (Buton ve Kutucuklar) yerleştiriyoruz
axbox_start = plt.axes([0.2, 0.05, 0.1, 0.075])
text_box_start = TextBox(axbox_start, 'Başlangıç: ', initial="0")

axbox_end = plt.axes([0.45, 0.05, 0.1, 0.075])
text_box_end = TextBox(axbox_end, 'Hedef: ', initial="49")

axbtn = plt.axes([0.6, 0.05, 0.2, 0.075])
btn = Button(axbtn, 'HESAPLA', color='lightgreen', hovercolor='0.975')
btn.on_clicked(hesapla)

#Program açıldığında kullanıcıya talimat veriyoruz
haritayi_ciz(sonuc_metni="Lütfen düğüm seçip hesaplayın.")
plt.show()