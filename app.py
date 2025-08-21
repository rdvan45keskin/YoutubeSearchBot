import sys
import time
from PyQt5 import QtWidgets
from HubForm import Ui_MainWindow
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QInputDialog

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

class FilterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Filter")

        layout = QVBoxLayout(self)

        self.comboBox = QComboBox(self)
        self.comboBox.addItems(["Relevance", "Upload Date", "View Count"])
        layout.addWidget(self.comboBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def get_selection(self):
        return self.comboBox.currentIndex() + 1

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.url = "https://www.youtube.com/"
        self.service = Service(ChromeDriverManager().install())
        self.driver = None

        self.ui.btn_start.clicked.connect(self.main)
        self.ui.btn_sort.clicked.connect(self.filter_progress)
        self.ui.btn_play.clicked.connect(self.play_button_click)
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_reSearch.clicked.connect(self.re_search)
        self.ui.VideoList.itemDoubleClicked.connect(self.play_video)

    def close(self):
        if self.driver:
            self.driver.quit()
        super().close()

    def filter_progress(self):
        dialog = FilterDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.filter(dialog.get_selection())

    def login_youtube(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(EC.url_contains("youtube.com"))

    def search(self, searchKey):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="center"]/yt-searchbox/div[1]/form/input'))
            )
            youtube_search = self.driver.find_element(By.XPATH, '//*[@id="center"]/yt-searchbox/div[1]/form/input')
            youtube_search.click()
            youtube_search.clear()
            youtube_search.send_keys(searchKey + Keys.ENTER)
        except Exception as ex:
            print(f"Search box not found: {ex}")
            self.close()
            exit()

    def filter(self, value):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='filter-button']/ytd-button-renderer/yt-button-shape/button"))
            ).click()
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/ytd-search-filter-options-dialog-renderer/div[2]/ytd-search-filter-group-renderer[5]/ytd-search-filter-renderer[{value}]/a"))
            ).click()
            self.results()
        except Exception as ex:
            print(f"Filter could not be applied: {ex}")
            self.close()
            exit()

    def results(self):
        try:
            time.sleep(2)
            video_list = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]")
            results = video_list.find_elements(By.XPATH, "//a[@id='video-title']")
            channels = video_list.find_elements(By.XPATH, "//*[@id='channel-info']")

            self.ui.VideoList.clear()
            for video, channel in zip(results, channels):
                item_text = f"Title: {video.text} - Channel: {channel.text}"
                self.ui.VideoList.addItem(item_text)

            if not results:
                print("No results found.")
        except Exception as ex:
            print(f"Could not fetch results: {ex}")

    def play_button_click(self):
        item = self.ui.VideoList.currentItem()
        if item:
            self.play_video(item)
        else:
            print("No video selected.")

    def play_video(self, item):
        try:
            item_text = item.text()
            selectedIndex = self.ui.VideoList.row(item)
            video_elements = self.driver.find_elements(By.XPATH, "//a[@id='video-title']")

            if video_elements and 0 <= selectedIndex < len(video_elements):
                choosen = video_elements[selectedIndex]
                choosen_link = choosen.get_attribute("href")

                self.ui.VideoList.clear()
                self.ui.VideoList.addItem(item_text)

                if choosen_link:
                    self.driver.get(choosen_link)
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )
                    print("Video loaded successfully.")
                else:
                    print("No link found for video.")
            else:
                print("Invalid video selection.")
        except Exception as ex:
            print(f"Error while playing video: {ex}")
            self.driver.quit()

    def main(self):
        self.driver = uc.Chrome()
        self.driver.maximize_window()
        self.login_youtube()
        searchKey, ok = QInputDialog.getText(self, "Search", "Enter keyword:")
        if ok:
            self.search(searchKey)
        self.results()

    def re_search(self):
        searchKey, ok = QInputDialog.getText(self, "Search", "Enter keyword:")
        if ok:
            self.search(searchKey)
        self.results()

def app():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app()
