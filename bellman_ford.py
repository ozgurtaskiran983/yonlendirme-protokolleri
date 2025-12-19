import networkx as nx
import matplotlib.pyplot as plt

class AgSimulasyonuBellman:
    def __init__(self):
        #NetworkX kütüphanesini kullanarak boş bir grafik oluşturuyoruz
        #Bu grafik yönlendirilmemiş (undirected) olacak, yani kablolar çift yönlüdür
        self.graph = nx.Graph() 

    def baglanti_ekle(self, u, v, agirlik):
        #İki yönlendirici (router) arasına belirtilen gecikme süresiyle (ağırlık) hat çekiyoruz
        self.graph.add_edge(u, v, weight=agirlik)

    def bellman_ford_kendi_kodumuz(self, baslangic_dugumu, hedef_dugumu):
        """
        Bellman-Ford Algoritması:
        Tüm kenarları (V-1) kez gezerek en kısa yolu bulmaya çalışır.
        """
        #1. BAŞLANGIÇ DURUMU (INITIALIZATION)
        #Tüm düğümlere olan mesafeyi başlangıçta sonsuz kabul ediyoruz
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        
        #Başlangıç noktasının kendine olan uzaklığı 0'dır
        mesafeler[baslangic_dugumu] = 0
        
        #En kısa yolu geriye doğru takip edebilmek için 'önceki düğüm' kaydı tutuyoruz
        onceki_dugum = {node: None for node in self.graph.nodes}
        
        #Toplam yönlendirici (düğüm) sayısını alıyoruz
        dugum_sayisi = self.graph.number_of_nodes()

        #2. GEVŞETME (RELAXATION) ADIMI
        #Bellman-Ford mantığı gereği, en kısa yol en fazla (Düğüm Sayısı - 1) kenardan oluşabilir
        #Bu yüzden tüm kenarları bu sayı kadar döngüye sokup kontrol ediyoruz
        for i in range(dugum_sayisi - 1):
            degisim_var = False #Bu turda herhangi bir iyileştirme yaptık mı kontrolü
            
            #Ağdaki tüm bağlantıları (kenarları) ve ağırlıklarını tek tek geziyoruz
            for u, v, data in self.graph.edges(data=True):
                agirlik = data['weight']
                
                #Ağımız yönsüz olduğu için hatlar iki taraflı çalışır
                #Bu yüzden hem u->v hem de v->u yönünü kontrol etmemiz gerekir
                
                #YÖN 1: u üzerinden v'ye gitmek, bildiğimiz yoldan daha kısaysa güncelle
                if mesafeler[u] != float('infinity') and mesafeler[u] + agirlik < mesafeler[v]:
                    mesafeler[v] = mesafeler[u] + agirlik
                    onceki_dugum[v] = u
                    degisim_var = True
                
                #YÖN 2: v üzerinden u'ya gitmek, bildiğimiz yoldan daha kısaysa güncelle
                if mesafeler[v] != float('infinity') and mesafeler[v] + agirlik < mesafeler[u]:
                    mesafeler[u] = mesafeler[v] + agirlik
                    onceki_dugum[u] = v
                    degisim_var = True
            
            #Eğer bu turda hiçbir mesafeyi kısaltamadıysak, işlem erken bitmiş demektir
            #Boşuna döngünün bitmesini beklemeye gerek yok (Optimizasyon)
            if not degisim_var:
                break

        #3. NEGATİF DÖNGÜ KONTROLÜ
        #Mühendislik açısından önemli: Eğer döngü bittiği halde hala kısalan yol varsa
        #sistemde negatif ağırlıklı bir döngü var demektir
        for u, v, data in self.graph.edges(data=True):
            agirlik = data['weight']
            if mesafeler[u] + agirlik < mesafeler[v]:
                print("UYARI: Negatif ağırlıklı döngü tespit edildi!")
                return None, None

        #4. ROTAYI OLUŞTURMA
        #Hedef düğümden başlayıp geriye, başlangıç düğümüne kadar gidiyoruz
        yol = []
        adim = hedef_dugumu
        
        #Eğer hedefe ulaşmak mümkün değilse (sonsuz mesafe)
        if mesafeler[hedef_dugumu] == float('infinity'):
            return None, float('infinity')

        while adim is not None:
            yol.insert(0, adim) #Düğümü listenin başına ekle
            adim = onceki_dugum[adim] #Bir önceki düğüme geç
            
        return yol, mesafeler[hedef_dugumu]

    def agi_ciz(self, bulunan_yol=None):
        #Grafiği ekrana çizdirmek için yerleşim düzenini ayarlıyoruz
        pos = nx.spring_layout(self.graph, seed=42)
        plt.figure(figsize=(10, 7))
        
        #Tüm düğümleri çiziyoruz, Bellman-Ford için yeşil renk tercih ettik
        nx.draw(self.graph, pos, with_labels=True, node_color='lightgreen', 
                node_size=2000, font_size=10, font_weight='bold')
        
        #Kenarların üzerine ağırlık (gecikme) değerlerini yazdırıyoruz
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        #Eğer algoritma bir yol bulduysa, o yolu kırmızı ile işaretliyoruz
        if bulunan_yol:
            path_edges = list(zip(bulunan_yol, bulunan_yol[1:]))
            nx.draw_networkx_nodes(self.graph, pos, nodelist=bulunan_yol, node_color='red')
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='red', width=2)

        plt.title("Ağ Topolojisi ve En Kısa Yol (Bellman-Ford)")
        plt.show()

#TEST KISMI
if __name__ == "__main__":
    sim = AgSimulasyonuBellman()
    
    #Dijkstra örneğindeki aynı ağ yapısını kuruyoruz ki sonuçları kıyaslayabilelim
    #A, B, C, D, E gibi routerları ve aralarındaki gecikmeleri ekliyoruz
    sim.baglanti_ekle('A', 'B', 4)
    sim.baglanti_ekle('A', 'C', 2)
    sim.baglanti_ekle('B', 'C', 1)
    sim.baglanti_ekle('B', 'D', 5)
    sim.baglanti_ekle('C', 'D', 8)
    sim.baglanti_ekle('C', 'E', 10)
    sim.baglanti_ekle('D', 'E', 2)
    sim.baglanti_ekle('D', 'Z', 6)
    sim.baglanti_ekle('E', 'Z', 3)

    print("Ağ oluşturuldu. Bellman-Ford algoritması ile en kısa yol hesaplanıyor...")
    
    try:
        #A noktasından Z noktasına giden en kısa yolu ve maliyetini istiyoruz
        yol, maliyet = sim.bellman_ford_kendi_kodumuz('A', 'Z')
        
        if yol:
            print(f"En Kısa Yol: {yol}")
            print(f"Toplam Maliyet (Gecikme): {maliyet} ms")
            #Sonucu görselleştirmek için grafiği çizdiriyoruz
            sim.agi_ciz(yol)
        else:
            print("Hedefe ulaşılamadı.")
            
    except Exception as e:
        print(f"Hata: {e}")