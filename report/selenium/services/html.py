from datetime import datetime

class Html:
    def get_html(self):
        print("getting html")
        page_source = self.driver.page_source

        current_time_str = datetime.now().strftime('%Y-%m-%d-%H-%M')
        filename = f"Tock-{current_time_str}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)