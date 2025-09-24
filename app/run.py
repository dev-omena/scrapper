try:
    from scraper.frontend import Frontend
except ImportError:
    from app.scraper.frontend import Frontend


def main():

    app = Frontend()
    app.root.protocol("WM_DELETE_WINDOW", app.closingbrowser)
    app.root.mainloop()


if __name__ == "__main__":
    main()
