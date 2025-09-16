import sys
import requests # Make sure you have this installed: pip install requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar,
    QAction, QLineEdit, QWidget, QVBoxLayout, QInputDialog,
    QMessageBox
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtNetwork import QNetworkProxy

# Use a test URL that is known to work well for checking proxy
TEST_URL = "http://httpbin.org/ip"
GEONODE_API_URL = "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=1&sort_by=lastChecked&sort_type=desc"


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("https://www.google.com"))

        self.layout.addWidget(self.webview)
        self.setLayout(self.layout)

    def navigate_to(self, url):
        if not url.startswith("http"):
            url = "http://" + url
        self.webview.setUrl(QUrl(url))


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(lambda: self.add_new_tab())
        # Move this line: self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        self.add_new_tab()

        # Navigation Bar
        self.navigation_bar = QToolBar("Navigation")
        self.addToolBar(self.navigation_bar)

        self.back_button = QAction("Back", self)
        self.back_button.triggered.connect(self.back_page)
        self.navigation_bar.addAction(self.back_button)

        self.forward_button = QAction("Forward", self)
        self.forward_button.triggered.connect(self.forward_page)
        self.navigation_bar.addAction(self.forward_button)

        self.reload_button = QAction("Reload", self)
        self.reload_button.triggered.connect(self.reload_page)
        self.navigation_bar.addAction(self.reload_button)

        self.home_button = QAction("Home", self)
        self.home_button.triggered.connect(self.go_home)
        self.navigation_bar.addAction(self.home_button)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.url_bar)

        # Connect the signal *after* all widgets have been created
        self.tabs.currentChanged.connect(self.update_url_bar)

        # Proxy action button
        self.find_proxy_action = QAction("Find Proxy", self)
        self.find_proxy_action.triggered.connect(self.find_and_set_proxy)
        self.navigation_bar.addAction(self.find_proxy_action)

    def current_webview(self):
        return self.tabs.currentWidget().webview if self.tabs.currentWidget() else None

    def add_new_tab(self, qurl=QUrl("https://www.google.com"), label="New Tab"):
        browser_tab = BrowserTab()
        self.tabs.addTab(browser_tab, label)
        self.tabs.setCurrentWidget(browser_tab)
        browser_tab.webview.urlChanged.connect(lambda qurl, browser_tab=browser_tab: self.update_url(qurl, browser_tab))

    def update_url(self, qurl, browser_tab):
        if self.tabs.currentWidget() == browser_tab:
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def update_url_bar(self, index):
        if self.tabs.currentWidget():
            qurl = self.tabs.currentWidget().webview.url()
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if self.current_webview():
            self.current_webview().setUrl(QUrl(url))

    def back_page(self):
        if self.current_webview():
            self.current_webview().back()

    def forward_page(self):
        if self.current_webview():
            self.current_webview().forward()

    def reload_page(self):
        if self.current_webview():
            self.current_webview().reload()

    def go_home(self):
        if self.current_webview():
            self.current_webview().setUrl(QUrl("https://www.google.com"))

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def find_and_set_proxy(self):
        """
        Fetches a list of proxies from GeoNode API, tests each one,
        and applies the first working one to the application.
        """
        QMessageBox.information(self, "Finding Proxy", "Attempting to find and apply a working proxy...")
        
        try:
            response = requests.get(GEONODE_API_URL, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            proxy_data = response.json()
            proxies = proxy_data.get("data", [])

            if not proxies:
                QMessageBox.warning(self, "Proxy Not Found", "The GeoNode API did not return any proxies.")
                return

            working_proxy_found = False
            for p in proxies:
                host = p.get("ip")
                port = int(p.get("port"))
                
                if not host or not port:
                    continue

                try:
                    # Set the proxy for testing
                    test_proxy = QNetworkProxy(QNetworkProxy.HttpProxy, host, port)
                    QNetworkProxy.setApplicationProxy(test_proxy)
                    
                    # Test the proxy by making a request
                    test_response = requests.get(TEST_URL, proxies={'http': f'http://{host}:{port}', 'https': f'https://{host}:{port}'}, timeout=5)
                    test_response.raise_for_status()
                    
                    # If the request is successful, the proxy works
                    QMessageBox.information(self, "Proxy Set", f"Found and applied a working proxy: {host}:{port}")
                    working_proxy_found = True
                    break # Stop after finding the first working proxy
                    
                except (requests.exceptions.RequestException, ValueError) as e:
                    print(f"Proxy {host}:{port} failed: {e}")
                    continue

            if not working_proxy_found:
                QMessageBox.warning(self, "Proxy Failed", "Could not find a working proxy from the list.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"Failed to fetch proxy list: {e}")
        except (ValueError, KeyError) as e:
            QMessageBox.critical(self, "JSON Parsing Error", f"Failed to parse proxy data: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())