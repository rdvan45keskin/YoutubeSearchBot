import sys
from PyQt5 import QtWidgets
from HubForm import Ui_MainWindow
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QInputDialog, QMessageBox, QListWidget

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class FilterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filtre Seçimi")

        # Layout
        layout = QVBoxLayout(self)

        # ComboBox
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(["Alaka Düzeyi", "Yüklenme Tarihi", "Görüntülenme Sayısı"])
        layout.addWidget(self.comboBox)

        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def get_selection(self):
        return self.comboBox.currentIndex() + 1

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # selenium init
        self.url = "https://www.youtube.com/"
        self.service = Service(ChromeDriverManager().install())
        self.driver = None
        
        self.ui.btn_start.clicked.connect(self.main)
        self.ui.btn_sort.clicked.connect(self.filter_progress)
        self.ui.btn_play.clicked.connect(self.play_button_click)
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_reSearch.clicked.connect(self.re_search)
        self.ui.VideoList.itemDoubleClicked.connect(self.play_video)  # Liste öğesine çift tıklama sinyali

    def close(self):
        if self.driver:
            self.driver.quit()
        super().close()

    def filter_progress(self):
        dialog = FilterDialog()
        result = dialog.exec_()
        print(f"Dialog result: {result}")
        if result == QDialog.Accepted:
            selected_value = dialog.get_selection()
            print(f"Selected filter value: {selected_value}")
            self.filter(selected_value)
        else:
            print("Filter selection was canceled.")

    def login_youtube(self):
        self.driver.get(self.url)
        # try:
        #     WebDriverWait(self.driver, 5).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, "gLFyf"))
        #     )
        #     input_element = self.driver.find_element(By.CLASS_NAME, "gLFyf")
        #     input_element.clear()
        #     input_element.send_keys("YouTube" + Keys.ENTER)
        # except Exception as ex:
        #     print(f"Google arama sayfası yüklenemedi: {ex}")
        #     self.close()
        #     exit()

        #     # YouTube linkine tıklama
        # try:
        #     WebDriverWait(self.driver, 5).until(
        #         EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "YouTube"))
        #     )
        #     link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "YouTube")
        #     link.click()
        # except Exception as ex:
        #     print(f"YouTube linki tıklanamadı: {ex}")
        #     self.close()
        #     exit()
        # Wait for navigation to YouTube
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("youtube.com")
        )
    
    def search(self,searchKey):
        # YouTube'da arama yapma
        try:
            WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="center"]/yt-searchbox/div[1]/form/input'))
            )
            youtube_search = self.driver.find_element(By.XPATH, '//*[@id="center"]/yt-searchbox/div[1]/form/input')
            youtube_search.click()
            youtube_search.clear()
            youtube_search.send_keys(searchKey + Keys.ENTER)
        except Exception as ex:
            print(f"YouTube arama kutusu bulunamadı: {ex}")
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
        self.results()

    def results(self):
        try:
            time.sleep(2)
            video_list = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]")
            results = video_list.find_elements(By.XPATH, "//a[@id='video-title']")
            channels = video_list.find_elements(By.XPATH, "//*[@id='channel-info']")

            # results = self.driver.find_elements(By.XPATH, "//*[@id='video-title']")
            # channels = self.driver.find_elements(By.XPATH, "//*[@id='channel-info']")
            
            # VideoList'i temizleme ve sonuçları ekleme
            self.ui.VideoList.clear()  # Daha önceki sonuçları temizle
            for video, channel in zip(results, channels):
                item_text = f"Video Başlığı: {video.text} - Kanal: {channel.text}"
                self.ui.VideoList.addItem(item_text)
            
            # VideoList'teki seçimden sonra işleme devam etme
            if results:
                self.ui.VideoList.itemDoubleClicked.connect(self.play_video)
            else:
                print("Sonuç bulunamadı.")
        except Exception as ex:
            print(f"Sonuçlar alınamadı veya video açılamadı: {ex}")

    def play_button_click(self):
        item = self.ui.VideoList.currentItem()
        if item:
            self.play_video(item)
        else:
            print("Seçili bir video bulunamadı.")

    def play_video(self, item):
        try:
            item_text = item.text()
            print(f"Seçilen öğe metni: '{item_text}'")

            selectedIndex = self.ui.VideoList.row(item)
            video_elements = self.driver.find_elements(By.XPATH, "//a[@id='video-title']")

            if video_elements and 0 <= selectedIndex < len(video_elements):
                choosen = video_elements[selectedIndex]
                choosen_link = choosen.get_attribute("href")

                # Seçilen videonun başlığını listeye ekleyin
                self.ui.VideoList.clear()
                self.ui.VideoList.addItem(item_text)

                if choosen_link:
                    self.driver.get(choosen_link)
                    print(f"Video linki açılıyor: {choosen_link}")

                    # Dinamik bir bekleme kullanarak, sayfanın yüklenip yüklenmediğini kontrol edin
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.TAG_NAME, "video"))
                        )
                        print("Video başarılı şekilde açıldı.")
                    except Exception as ex:
                        print(f"Video yüklenemedi: {ex}")
                        return

                    # # Kullanıcıya video oynayıp oynamadığını sormak için bir mesaj kutusu gösterin
                    # msg = QMessageBox.question(self, "Onay Panosu", "Video Başladı Mı?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    # if msg == QMessageBox.Yes:
                    #     print("Kullanıcı videonun başladığını onayladı.")
                    # elif msg == QMessageBox.No:
                    #     screen = self.driver.find_element(By.TAG_NAME, "body")
                    #     screen.send_keys("k")  # Video durdurmak veya oynatmak için 'k' tuşunu kullanın
                    # else:
                    #     print("Geçersiz veri")
                else:
                    print("Video için href bulunamadı.")
            else:
                print("Seçilen indeks, mevcut video listesinin dışında.")
        
        except Exception as ex:
            print(f"Bir hata oluştu: {ex}")
            self.driver.quit()  # Tarayıcıyı kapatma işlemi



    def main(self):
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.login_youtube()
        searchKey, ok = QInputDialog.getText(self, "Input", "Enter something:")
        if ok:
            print(f"User input: {searchKey}")
            self.search(searchKey)
        self.results()

    def re_search(self):
        searchKey, ok = QInputDialog.getText(self, "Input", "Enter something:")
        if ok:
            print(f"User input: {searchKey}")
            self.search(searchKey)
        self.results()

def app():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app()
