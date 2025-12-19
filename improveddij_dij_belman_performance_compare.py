import networkx as nx
import matplotlib.pyplot as plt
import heapq
import time
import random

class AgSimulasyonu:
    def __init__(self):
        #NetworkX kütüphanesi ile boş bir ağ yapısı oluşturuyoruz
        self.graph = nx.Graph()

    def baglanti_ekle(self, u, v, agirlik, trafik=0):
        #Düğümler arasına hem mesafeyi (ağırlık) hem de trafik verisini ekliyoruz
        self.graph.add_edge(u, v, weight=agirlik, traffic=trafik)

    def dijkstra_kendi_kodumuz(self, baslangic, hedef):
        #Klasik Dijkstra: Sadece fiziksel mesafeyi (weight) baz alır, trafiği görmez
        #Başlangıçta tüm mesafeleri sonsuz yapıyoruz
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        
        #Öncelik kuyruğuna (Priority Queue) başlangıç düğümünü ekliyoruz
        pq = [(0, baslangic)]
        
        while pq:
            #Kuyruktan en kısa mesafeli düğümü çekiyoruz
            mevcut_mesafe, mevcut_dugum = heapq.heappop(pq)
            
            #Hedefe ulaştıysak döngüyü bitiriyoruz
            if mevcut_dugum == hedef: break
            
            #Daha kısa bir yol zaten bulduysak bunu atlıyoruz
            if mevcut_mesafe > mesafeler[mevcut_dugum]: continue
            
            #Komşuları geziyoruz
            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                agirlik = ozellikler['weight']
                yeni_mesafe = mevcut_mesafe + agirlik
                
                #Daha kısa bir yol bulduysak güncelliyoruz
                if yeni_mesafe < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_mesafe
                    heapq.heappush(pq, (yeni_mesafe, komsu))
        return mesafeler[hedef]

    def modifiye_dijkstra(self, baslangic, hedef):
        #Geliştirdiğimiz algoritmamız mesafe ile birlikte trafik yoğunluğunu da hesaba katar
        CEZA_KATSAYISI = 10.0
        mesafeler = {node: float('infinity') for node in self.graph.nodes}
        mesafeler[baslangic] = 0
        pq = [(0, baslangic)]
        
        while pq:
            mevcut_maliyet, mevcut_dugum = heapq.heappop(pq)
            if mevcut_dugum == hedef: break
            if mevcut_maliyet > mesafeler[mevcut_dugum]: continue

            for komsu, ozellikler in self.graph[mevcut_dugum].items():
                mesafe = ozellikler['weight']
                #Trafik verisi varsa alıyoruz, yoksa 0 kabul ediyoruz
                trafik = ozellikler.get('traffic', 0) 
                
                #Trafik varsa yolu sanal olarak uzatıp (ceza verip) oradan kaçmasını sağlıyoruz
                #İşlemci burada fazladan matematiksel işlem (çarpma) yapıyor
                efektif_maliyet = mesafe * (1 + (trafik * CEZA_KATSAYISI))
                
                yeni_maliyet = mevcut_maliyet + efektif_maliyet
                if yeni_maliyet < mesafeler[komsu]:
                    mesafeler[komsu] = yeni_maliyet
                    heapq.heappush(pq, (yeni_maliyet, komsu))
        return mesafeler[hedef]

#TEST VE PERFORMANS FONKSİYONLARI
def rastgele_ag_olustur(dugum_sayisi, baglanti_ihtimali=0.3):
    #Performans testi için rastgele büyüklükte bir ağ ve trafik verisi üretiyoruz
    G = nx.erdos_renyi_graph(dugum_sayisi, baglanti_ihtimali, seed=42)
    
    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = random.randint(1, 100)
        #Gerçekçi olması için her yola 0 ile 1 arasında rastgele trafik atıyoruz
        G.edges[u, v]['traffic'] = random.uniform(0, 1)
    
    sim = AgSimulasyonu()
    sim.graph = G
    return sim

def performansi_karsilastir():
    print("3'lü Performans Testi Başlıyor")
    
    #Algoritmaları zorlamak için 20'den 500'e kadar artan düğüm sayıları kullanıyoruz
    dugum_sayilari = [20, 50, 100, 200, 300, 500] 
    
    dijkstra_sureleri = []
    bellman_ford_sureleri = []
    modifiye_sureleri = [] 

    for n in dugum_sayilari:
        print(f"{n} Router'lı ağ üzerinde test yapılıyor...")
        
        #Her turda yeni ve daha büyük bir ağ oluşturuyoruz
        sim = rastgele_ag_olustur(n)
        start_node = 0
        target_node = n - 1
        
        #1. Klasik Dijkstra'nın süresini ölçüyoruz
        t0 = time.time()
        try: sim.dijkstra_kendi_kodumuz(start_node, target_node)
        except: pass
        t1 = time.time()
        dijkstra_sureleri.append(t1 - t0)

        #2. Geliştirdiğimiz modifiyeli Dijkstra'nın süresini ölçüyoruz
        t0 = time.time()
        try: sim.modifiye_dijkstra(start_node, target_node)
        except: pass
        t1 = time.time()
        modifiye_sureleri.append(t1 - t0)

        #3. Kıyaslama için Bellman-Ford'u da ölçüyoruz
        t0 = time.time()
        try: nx.bellman_ford_path_length(sim.graph, start_node, target_node)
        except: pass
        t1 = time.time()
        bellman_ford_sureleri.append(t1 - t0)

    #Test sonuçlarını grafik üzerinde gösteriyoruz
    plt.figure(figsize=(12, 7))
    
    #Bellman-Ford kırmızı ve kesikli çizgiyle gösterdik
    plt.plot(dugum_sayilari, bellman_ford_sureleri, marker='x', label='Bellman-Ford', color='red', linestyle='--', linewidth=2)
    #Klasik Dijkstra mavi düz çizgiyle gösterdik
    plt.plot(dugum_sayilari, dijkstra_sureleri, marker='o', label='Klasik Dijkstra', color='blue', linewidth=2)
    #Bizim algoritmamız yeşil çizgiyle gösterdik
    plt.plot(dugum_sayilari, modifiye_sureleri, marker='s', label='Geliştirilmiş Dijkstra', color='green', linestyle='-', linewidth=2, alpha=0.7)
    
    plt.title("3 Algoritmanın Performans Karşılaştırması", fontsize=14)
    plt.xlabel("Ağdaki Router Sayısı (Düğüm)", fontsize=12)
    plt.ylabel("Hesaplama Süresi (Saniye)", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.show()
    print("Test tamamlandı!")

if __name__ == "__main__":
    performansi_karsilastir()