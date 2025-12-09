class DashboardController:
    def __init__(self):
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def display(self):
        for widget in self.widgets:
            widget.render()