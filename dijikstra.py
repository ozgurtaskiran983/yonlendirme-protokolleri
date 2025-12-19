import networkx as nx
import matplotlib.pyplot as plt
import heapq #Öncelik kuyruğu Dijkstra algoritmasının kalbidir

class AgSimulasyonu:
    def __init__(self):
        #NetworkX kütüphanesini kullanarak boş bir ağ yapısı oluşturuyoruz
        self.graph = nx.Graph()

    def baglanti_ekle(self, u, v, agirlik):
        #İki yönlendirici (router) arasına belirtilen gecikme süresiyle kablo çekiyoruz
        self.graph.add_edge(u, v, weight=agirlik)

    def dijkstra_kendi_kodumuz(self, baslangic_dugumu, hedef_dugumu):
        """
        Dijkstra Algoritmasının Adım Adım Uygulanması
        """
        #BAŞLANGIÇ AYARLARI
        #Başlangıçta tüm düğümlere olan mesafeyi sonsuz kabul ediyoruz
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        #Sadece başlangıç noktasının kendine olan uzaklığı 0'dır
        mesafeler[baslangic_dugumu] = 0
        
        #En kısa yolu bulduğumuzda geriye doğru takip edebilmek için kayıt tutuyoruz
        onceki_dugum = {node: None for node in self.graph.nodes}
        
        #Öncelik kuyruğunu (Priority Queue) başlatıyoruz ve başlangıç düğümünü ekliyoruz
        #Bu yapı her zaman en kısa mesafeli düğümü bize ilk sırada verir
        pq = [(0, baslangic_dugumu)]

        while pq:
            #Kuyruktan en küçük mesafeye sahip düğümü çekip işlemeye başlıyoruz
            mevcut_mesafe, mevcut_dugum = heapq.heappop(pq)

            #Eğer hedef düğüme ulaştıysak döngüyü erkenden bitirebiliriz
            if mevcut_dugum == hedef_dugumu:
                break

            #Eğer kuyruktan gelen mesafe bildiğimiz yoldan daha uzunsa bu adımı atlıyoruz
            if mevcut_mesafe > mesafeler[mevcut_dugum]:
                continue

            #Mevcut düğümün tüm komşularını tek tek kontrol ediyoruz
            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                agirlik = ozellikler['weight']
                yeni_mesafe = mevcut_mesafe + agirlik

                #Eğer bu komşuya giden daha kısa bir yol bulduysak bilgileri güncelliyoruz
                if yeni_mesafe < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_mesafe
                    onceki_dugum[komsu] = mevcut_dugum
                    #Yeni bulduğumuz kısa yolu kuyruğa ekliyoruz
                    heapq.heappush(pq, (yeni_mesafe, komsu))
        
        #ROTAYI OLUŞTURMA
        #Hedef düğümden başlayıp geriye doğru (start noktasına kadar) gidiyoruz
        yol = []
        adim = hedef_dugumu
        while adim is not None:
            yol.insert(0, adim) #Düğümü listenin başına ekle
            adim = onceki_dugum[adim] #Bir önceki adıma git
            
        return yol, mesafeler[hedef_dugumu]

    def agi_ciz(self, bulunan_yol=None):
        #Grafiğin ekranda düzgün görünmesi için yaylı yerleşim algoritması kullanıyoruz
        pos = nx.spring_layout(self.graph, seed=42) 
        
        plt.figure(figsize=(10, 7))
        
        #Tüm düğümleri mavi renkli ve etiketli olarak çiziyoruz
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, font_size=10, font_weight='bold')
        
        #Bağlantıların üzerindeki ağırlık (gecikme) değerlerini yazdırıyoruz
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        #Eğer algoritma bir yol bulduysa o yolu kırmızı renk ile belirginleştiriyoruz
        if bulunan_yol:
            path_edges = list(zip(bulunan_yol, bulunan_yol[1:]))
            nx.draw_networkx_nodes(self.graph, pos, nodelist=bulunan_yol, node_color='red')
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='red', width=2)

        plt.title("Ağ Topolojisi ve En Kısa Yol (Dijkstra)")
        plt.show()

#TEST KISMI
if __name__ == "__main__":
    sim = AgSimulasyonu()
    
    #Test için örnek bir ağ topolojisi oluşturuyoruz
    #Router isimleri ve aralarındaki gecikme sürelerini (ms) ekliyoruz
    sim.baglanti_ekle('A', 'B', 4)
    sim.baglanti_ekle('A', 'C', 2)
    sim.baglanti_ekle('B', 'C', 1)
    sim.baglanti_ekle('B', 'D', 5)
    sim.baglanti_ekle('C', 'D', 8)
    sim.baglanti_ekle('C', 'E', 10)
    sim.baglanti_ekle('D', 'E', 2)
    sim.baglanti_ekle('D', 'Z', 6)
    sim.baglanti_ekle('E', 'Z', 3)

    print("Ağ oluşturuldu. Dijkstra algoritması çalıştırılıyor...")
    
    #A noktasından Z noktasına giden en kısa yolu hesaplatıyoruz
    try:
        yol, maliyet = sim.dijkstra_kendi_kodumuz('A', 'Z')
        print(f"En Kısa Yol: {yol}")
        print(f"Toplam Maliyet (Gecikme): {maliyet} ms")
        
        #Sonucu görselleştirmek için grafiği ekrana veriyoruz
        sim.agi_ciz(yol)
        
    except Exception as e:
        print(f"Hata: {e}")