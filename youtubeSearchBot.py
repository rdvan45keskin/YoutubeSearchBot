from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
class GOOGLE:
    def __init__(self):
        self.url = "https://www.google.com"
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        
    def search_youtube(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gLFyf"))
            )
            input_element = self.driver.find_element(By.CLASS_NAME, "gLFyf")
            input_element.clear()
            input_element.send_keys("YouTube" + Keys.ENTER)
        except Exception as ex:
            print(f"Google arama sayfası yüklenemedi: {ex}")
            self.close()
            exit()

            # YouTube linkine tıklama
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "YouTube"))
            )
            link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "YouTube")
            link.click()
        except Exception as ex:
            print(f"YouTube linki tıklanamadı: {ex}")
            self.close()
            exit()
        # Wait for navigation to YouTube
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("youtube.com")
        )
    def get_driver(self):
        return self.driver
    
    def close(self):
        self.driver.quit()
        

class YOUTUBE:
    def __init__(self,key,driver):
        self.key = key
        self.driver = driver

    def search(self):
        # YouTube'da arama yapma
        try:
            WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#search'))
            )
            youtube_search = self.driver.find_element(By.CSS_SELECTOR, 'input#search')
            youtube_search.click()
            youtube_search.clear()
            youtube_search.send_keys(self.key + Keys.ENTER)
        except Exception as ex:
            print(f"YouTube arama kutusu bulunamadı: {ex}")
            self.close()
            exit()

        filter_value = input("1- Alaka düzeyi\n2- Yüklenme tarihi\n3- Görüntülenme sayısı\nSeçiminiz:\n")
        # Filtreleme işlemi
        if filter_value == "1":
            pass
        elif filter_value == "2":
            self.filter(2)
        elif filter_value == "3":
            self.filter(3)
        else:
            print("geçersiz filtre")
            self.close()
            exit()

    def filter(self,value):
        # Filtre butonu fonksiyonu
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='filter-button']/ytd-button-renderer/yt-button-shape/button"))
            ).click()
        except Exception as ex:
            print(f"Filtre butonuna tıklanamadı: {ex}")
            self.close()
            exit()
        # Filtre seçenekleri fonksiyonu
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/ytd-search-filter-options-dialog-renderer/div[2]/ytd-search-filter-group-renderer[5]/ytd-search-filter-renderer[{value}]/a"))
            ).click()
        except Exception as ex:
            print(f"Filtreleme seçeneği tıklanamadı: {ex}")
            self.close()
            exit()

    def results(self):
        # Sonuçları alma
        try:
            time.sleep(2)
            results = self.driver.find_elements(By.XPATH, "//*[@id='video-title']")
            channels = self.driver.find_elements(By.XPATH, "//*[@id='channel-info']")
            
            # Bulunan sonuçları konsolda text ile yazdırma
            for index, (video, channel) in enumerate(zip(results, channels), start=1):
                print(f"{index}. Video Başlığı: {video.text} - Kanal: {channel.text}")

            # Sonuç varsa:
            if results:
                while True:
                    choose = int(input("Videoyu seçin (numarayı girin): ")) - 1
                    if 0 <= choose < len(results):                                  # Seçilen numaranın geçerli olup olmadığını kontrol et
                        choosen = results[choose]                                   # Dizideki seçilen elemanı al ve choosen değişkenine ata
                        choosen_link = choosen.get_attribute("href")                # Href bilgisini yani linki al
                        if choosen_link:                                            # Link varsa:
                            self.driver.get(choosen_link)                                # Linki aç
                            time.sleep(2)                                           # 2 saniye bekleme
                            check = input("video başladı mı?(y/n)\n").lower()
                            if check == "y":
                                break
                            elif check == "n":
                                screen = self.driver.find_element(By.TAG_NAME,"body")    # Tüm sekmeyi al
                                screen.send_keys("k")                               # Video oynatma kısayolu k bas
                                break
                            else:
                                print("geçersiz veri")
                        else:
                            print("İlk video için href bulunamadı.")
                    else:
                        print("geçersiz seçim")
            else:
                print("Sonuç bulunamadı.")
        except Exception as ex:
            print(f"Sonuçlar alınamadı veya video açılamadı: {ex}")

    def close(self):
        self.driver.quit()

google_search = GOOGLE()
google_search.search_youtube()

while True:
    driver = google_search.get_driver()
    seach_key = input("aranacak kelimeyi yazın:\n")

    youtube = YOUTUBE(seach_key,driver)
    youtube.search()
    youtube.results()
    another = input("başka arama yapmak ister misiniz?(y/n)\n").lower()
    if another == "y":
        driver = google_search.get_driver()
        seach_key = input("aranacak kelimeyi yazın:\n")

        youtube = YOUTUBE(seach_key,driver)
        youtube.search()
        youtube.results()
    elif another == "n":
        # Tarayıcıyı kapatmadan açık bırakın veya devam etmek için manuel kapatma yapabilirsiniz
        input("Tarayıcıyı kapatmak için Enter'a basın...")
        driver.quit()
        exit()                  
    else:
        print("geçersiz veri")