import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar,
    QAction, QLineEdit, QWidget, QVBoxLayout, QInputDialog,
    QMessageBox
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtNetwork import QNetworkProxy


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
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        # Navigation bar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # Add the 'Go' button here
        go_btn = QAction("Go", self)
        go_btn.triggered.connect(self.navigate_to_url)
        nav_bar.addAction(go_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        nav_bar.addAction(new_tab_btn)
        
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.go_back)
        nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        nav_bar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        nav_bar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        nav_bar.addAction(home_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        nav_bar.addAction(new_tab_btn)

        # Proxy action
        proxy_btn = QAction("Set Proxy", self)
        proxy_btn.triggered.connect(self.set_proxy)
        nav_bar.addAction(proxy_btn)

        # Start with one tab
        self.add_new_tab(url="https://google.com")

    def add_new_tab(self, url="https://www.google.com"):
        browser_tab = BrowserTab()
        index = self.tabs.addTab(browser_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        browser_tab.webview.load(QUrl(url))
        browser_tab.webview.urlChanged.connect(lambda qurl: self.update_url_bar(qurl, browser_tab))
        browser_tab.webview.titleChanged.connect(lambda title: self.tabs.setTabText(self.tabs.indexOf(browser_tab), title))
    
    def current_webview(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            return current_widget.webview
        return None

    def navigate_to_url(self):
        url = self.url_bar.text()
        if self.current_webview():
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            self.current_webview().setUrl(QUrl(url))

    def update_url_bar(self, qurl=None, browser_tab=None):
        if not browser_tab:
            browser_tab = self.tabs.currentWidget()
        
        if browser_tab and browser_tab.webview.url() == self.tabs.currentWidget().webview.url():
            self.url_bar.setText(browser_tab.webview.url().toString())
            self.setWindowTitle(browser_tab.webview.title())

    def go_back(self):
        if self.current_webview():
            self.current_webview().back()

    def go_forward(self):
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

    def set_proxy(self):
        """
        Prompts the user for proxy details and sets the proxy for the entire application.
        """
        proxy_info, ok = QInputDialog.getText(self, "Set Proxy",
                                              "Enter proxy address and port (e.g., 127.0.0.1:8080):")
        if ok and proxy_info:
            try:
                host, port = proxy_info.split(':')
                port = int(port)
                
                proxy = QNetworkProxy(QNetworkProxy.HttpProxy, host, port)
                # Corrected line to set the proxy for the application
                QNetworkProxy.setApplicationProxy(proxy)
                
                QMessageBox.information(self, "Proxy Set", "Proxy settings have been applied.")
            except (ValueError, IndexError):
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid proxy address and port (e.g., 127.0.0.1:8080).")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())