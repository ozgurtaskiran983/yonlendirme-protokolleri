import networkx as nx
import matplotlib.pyplot as plt
import heapq
import random

class GelismisAgAnalizi:
    def __init__(self, dugum_sayisi=15):
        #Görselliğin temiz ve okunaklı olması için 15-20 arası düğüm sayısı idealdir
        #Erdos-Renyi modeli ile rastgele bağlantılara sahip bir ağ oluşturuyoruz
        self.graph = nx.erdos_renyi_graph(dugum_sayisi, 0.3, seed=42)
        
        #Ağdaki her bağlantıya (kabloya) rastgele bir gecikme süresi (ağırlık) atıyoruz
        for (u, v) in self.graph.edges():
            self.graph.edges[u, v]['weight'] = random.randint(1, 20)
            
    def dijkstra_analizli(self, baslangic, hedef):
        """
        Hem en kısa yolu bulur hem de algoritmanın kaç işlem yaptığını (eforunu) sayar.
        """
        islem_sayisi = 0
        
        #Başlangıçta tüm düğümlere olan mesafeyi sonsuz, başlangıç düğümünü 0 yapıyoruz
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        
        #Dijkstra'nın kalbi olan öncelik kuyruğunu başlatıyoruz
        pq = [(0, baslangic)]
        
        #Yolu geriye doğru takip edebilmek için kimden geldiğimizi not ediyoruz
        onceki = {node: None for node in self.graph.nodes}
        
        while pq:
            #Kuyruktan en düşük maliyetli düğümü çekiyoruz ve işlem sayacını artırıyoruz
            mevcut_mesafe, mevcut_dugum = heapq.heappop(pq)
            islem_sayisi += 1 

            #Eğer hedef düğüme ulaştıysak döngüyü bitiriyoruz
            if mevcut_dugum == hedef:
                break
            
            #Daha kısa bir yol zaten bulunduysa bu adımı atlıyoruz
            if mevcut_mesafe > mesafeler[mevcut_dugum]:
                continue
                
            #Mevcut düğümün tüm komşularını geziyoruz
            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                islem_sayisi += 1 #Her komşu kontrolü işlemci için bir yüktür, bunu sayıyoruz
                agirlik = ozellikler['weight']
                yeni_mesafe = mevcut_mesafe + agirlik
                
                #Daha kısa bir yol bulduysak bilgileri güncelliyoruz
                if yeni_mesafe < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_mesafe
                    onceki[komsu] = mevcut_dugum
                    heapq.heappush(pq, (yeni_mesafe, komsu))
        
        #ROTAYI OLUŞTURMA
        #Hedef düğümden başlayıp geriye, start noktasına kadar gidiyoruz
        yol = []
        curr = hedef
        while curr is not None:
            yol.insert(0, curr)
            curr = onceki[curr]
            
        return yol, mesafeler[hedef], islem_sayisi

    def bellman_ford_analizli(self, baslangic, hedef):
        """
        Bellman-Ford algoritmasının aynı yolu bulmak için ne kadar çok işlem yaptığını sayar.
        """
        islem_sayisi = 0
        
        #Başlangıç ayarları Dijkstra ile aynıdır
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        onceki = {node: None for node in self.graph.nodes}
        
        dugum_sayisi = self.graph.number_of_nodes()
        
        #Bellman-Ford mantığı: Tüm kenarları (Düğüm Sayısı - 1) kez gezmek zorundadır
        for _ in range(dugum_sayisi - 1):
            degisim_var = False
            
            #Ağdaki bütün bağlantıları tek tek kontrol ediyoruz (Brute-Force yaklaşımı)
            for u, v, data in self.graph.edges(data=True):
                islem_sayisi += 1 #Her kenar kontrolü bir işlemdir
                
                #YÖN 1: u'dan v'ye gidiş kontrolü
                if mesafeler[u] + data['weight'] < mesafeler[v]:
                    mesafeler[v] = mesafeler[u] + data['weight']
                    onceki[v] = u
                    degisim_var = True
                
                #YÖN 2: v'den u'ya gidiş kontrolü (Yönsüz ağ olduğu için)
                if mesafeler[v] + data['weight'] < mesafeler[u]:
                    mesafeler[u] = mesafeler[v] + data['weight']
                    onceki[u] = v
                    degisim_var = True
                    
            #Eğer bu turda hiçbir güncelleme yapmadıysak işlemi erken bitiriyoruz
            if not degisim_var:
                break
                
        #Yolu oluşturuyoruz (Sadece karşılaştırma grafiğinde göstermek için)
        yol = []
        if mesafeler[hedef] != float('infinity'):
            curr = hedef
            while curr is not None and curr != baslangic:
                yol.insert(0, curr)
                curr = onceki[curr]
            yol.insert(0, baslangic)
            
        return yol, mesafeler[hedef], islem_sayisi

    def karsilastirmali_cizim(self, baslangic, hedef):
        #1. ANALİZ ADIMI
        #Her iki algoritmayı da çalıştırıp sonuçları ve işlem sayılarını alıyoruz
        d_yol, d_maliyet, d_islem = self.dijkstra_analizli(baslangic, hedef)
        b_yol, b_maliyet, b_islem = self.bellman_ford_analizli(baslangic, hedef)

        #2. GÖRSELLEŞTİRME ADIMI
        #Düğümlerin ekrandaki yerini sabitliyoruz
        pos = nx.spring_layout(self.graph, seed=42)
        plt.figure(figsize=(12, 8))
        
        #Ana ağ yapısını gri renkli ve etiketli olarak çiziyoruz
        nx.draw(self.graph, pos, with_labels=True, node_color='lightgrey', 
                node_size=1000, font_size=10, edge_color='gray')
        
        #Bağlantıların üzerine gecikme sürelerini (ağırlıkları) yazıyoruz
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        #Bulunan en kısa yolu yeşil düğümler ve kalın mor çizgi ile belirginleştiriyoruz
        path_edges = list(zip(d_yol, d_yol[1:]))
        nx.draw_networkx_nodes(self.graph, pos, nodelist=d_yol, node_color='#4CAF50', node_size=1100)
        nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='#5A25AF', width=4, label='En Kısa Yol')

        #3. SONUÇ TABLOSU
        #Algoritmaların performans karşılaştırmasını içeren bilgi kutusunu hazırlıyoruz
        bilgi_metni = (
            f"BAŞLANGIÇ: {baslangic} -> HEDEF: {hedef}\n\n"
            f"DIJKSTRA ALGORİTMASI\n"
            f"• Bulunan Maliyet: {d_maliyet} ms\n"
            f"• İşlem Sayısı (Efor): {d_islem} adım\n\n"
            f"BELLMAN-FORD ALGORİTMASI\n"
            f"• Bulunan Maliyet: {b_maliyet} ms\n"
            f"• İşlem Sayısı (Efor): {b_islem} adım\n\n"
            f"SONUÇ: Dijkstra aynı yolu {round(b_islem/d_islem, 1)} kat\ndaha az işlemle buldu!"
        )
        
        #Bilgi kutusunu grafiğin sağ üst köşesine yerleştiriyoruz
        plt.text(0.95, 0.95, bilgi_metni, transform=plt.gca().transAxes, fontsize=11,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

        plt.title(f"Aynı Ağ Üzerinde Algoritma Verimlilik Analizi", fontsize=14)
        plt.show()

#TEST KISMI
if __name__ == "__main__":
    #15 Router'lı örnek bir ağ oluşturup analizi başlatıyoruz
    analiz = GelismisAgAnalizi(dugum_sayisi=15) 
    #0 numaralı düğümden 14 numaralı düğüme giden yolu analiz ediyoruz
    analiz.karsilastirmali_cizim(0, 14)