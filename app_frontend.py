from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
import random
import string
import webbrowser

from google_sheets_backend import add_device, get_inventory_data

class BorderedLabel(Label):
    def __init__(self, **kwargs):
        self.theme_manager = kwargs.pop('theme_manager', None)
        super(BorderedLabel, self).__init__(**kwargs)
        with self.canvas.before:
            from kivy.graphics import Line, Color
            Color(0, 1, 0, 1)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_border, size=self.update_border)
        self.bind(size=self.update_text_size)
        self.update_theme()

    def update_border(self, *args):
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

    def update_text_size(self, *args):
        self.text_size = (self.width, self.height)

    def update_theme(self):
        if self.theme_manager:
            self.color = self.theme_manager.text_color

class BorderedButton(Button):
    def __init__(self, **kwargs):
        self.theme_manager = kwargs.pop('theme_manager', None)
        super(BorderedButton, self).__init__(**kwargs)
        with self.canvas.before:
            from kivy.graphics import Line, Color
            Color(0, 1, 0, 1)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_border, size=self.update_border)
        self.bind(size=self.update_text_size)
        self.update_theme()

    def update_border(self, *args):
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

    def update_text_size(self, *args):
        self.text_size = (self.width, self.height)

    def update_theme(self):
        if self.theme_manager:
            self.color = self.theme_manager.text_color

class ClickableLabel(ButtonBehavior, Label):
    pass

class ThemeManager:
    def __init__(self):
        self.is_light_mode = False
        self.text_color = (1, 1, 1, 1)
        self.background_color = (0, 0, 0, 1)

    def toggle_theme(self, is_light_mode):
        self.is_light_mode = is_light_mode
        if self.is_light_mode:
            self.text_color = (0, 0, 0, 1)
            self.background_color = (1, 1, 1, 1)
        else:
            self.text_color = (1, 1, 1, 1)
            self.background_color = (0, 0, 0, 1)
        Window.clearcolor = self.background_color

class HomePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = ThemeManager()
        self.orientation = 'vertical'
        self.inventory_data_cache = None
        self.auto_refresh_event = None
        self.font_size = 16
        self.language_code = 'en'

        self.init_text_variables()

        self.content_area = BoxLayout(orientation='vertical')
        self.add_widget(self.content_area)

        self.nav_bar = BoxLayout(size_hint_y=None, height=dp(60), orientation='horizontal')
        self.add_widget(self.nav_bar)

        self.inventory_button = ToggleButton(text=self.inventory_button_text, group='nav', on_press=self.show_inventory_page)
        self.add_device_button = ToggleButton(text=self.add_device_button_text, group='nav', on_press=self.show_add_device_page)
        self.settings_button = ToggleButton(text=self.settings_button_text, group='nav', on_press=self.show_settings_page)

        self.inventory_button.color = self.theme_manager.text_color
        self.add_device_button.color = self.theme_manager.text_color
        self.settings_button.color = self.theme_manager.text_color

        self.nav_bar.add_widget(self.inventory_button)
        self.nav_bar.add_widget(self.add_device_button)
        self.nav_bar.add_widget(self.settings_button)

        self.inventory_button.state = 'down'

        self.show_inventory_page()

    def init_text_variables(self):
        self.language_options = [
            {'code': 'en', 'name_en': 'English', 'name_es': 'Inglés'},
            {'code': 'es', 'name_en': 'Spanish', 'name_es': 'Español'},
        ]
        if self.language_code == 'en':
            self.language_values = [option['name_en'] for option in self.language_options]
        elif self.language_code == 'es':
            self.language_values = [option['name_es'] for option in self.language_options]

        self.language = self.get_language_display_name(self.language_code)

        if self.language_code == 'en':
            self.inventory_button_text = 'Inventory'
            self.add_device_button_text = 'Add Device'
            self.settings_button_text = 'Settings'

            self.inventory_page_title = 'Inventory List'
            self.add_device_page_title = 'Enter New Device Information'
            self.settings_page_title = 'Settings'
            self.details_page_title = 'Details for Item ID: {}'

            self.refresh_button_text = 'Refresh Inventory'
            self.submit_button_text = 'Submit'
            self.back_to_inventory_text = 'Back to Inventory'
            self.back_button_text = 'Back'
            self.save_settings_text = 'Save Settings'
            self.settings_saved_text = 'Settings Saved Successfully'
            self.device_added_text = 'Device Added Successfully'
            self.no_inventory_text = 'No inventory data available.'

            self.enable_light_mode_text = 'Enable Light Mode:'
            self.change_font_size_text = 'Change Font Size:'
            self.clear_cached_data_text = 'Clear Cached Data:'
            self.language_selection_text = 'Language Selection:'
            self.auto_refresh_interval_text = 'Auto-Refresh Interval (hours):'
            self.enable_auto_refresh_text = 'Enable Auto-Refresh:'
            self.clear_cache_button_text = 'Clear Cache'

            self.form_labels = {
                "Item Name:": "Item Name:",
                "Brand/Manufacturer:": "Brand/Manufacturer:",
                "Model Number:": "Model Number:",
                "Serial Number:": "Serial Number:",
                "Purchase Date (YYYY-MM-DD):": "Purchase Date (YYYY-MM-DD):",
                "Warranty Expiry (YYYY-MM-DD):": "Warranty Expiry (YYYY-MM-DD):",
                "Status:": "Status:",
                "Condition:": "Condition:",
                "Assigned To:": "Assigned To:",
                "Location:": "Location:",
                "Value (USD):": "Value (USD):",
                "Hardware Notes/Specifications:": "Hardware Notes/Specifications:",
                "Disposition:": "Disposition:",
                "Hardware Type:": "Hardware Type:",
                "Tech. Support:": "Tech. Support:",
                "Website:": "Website:",
                "Images URL:": "Images URL:"
            }

            self.status_values = ['Not In Use', 'In Use']
            self.condition_values = ['Unknown', 'Good Condition', 'Damaged']
            self.disposition_values = ['Keep', 'Salvage', 'Recycle', 'Trash']
            self.hardware_type_values = ['Printer', 'Scanner', 'Laptop', 'Phone', 'Desktop', 'Tablet', 'Server', 'Network Equipment', 'Other']
            self.font_size_options = [('Small', 12), ('Medium', 16), ('Large', 20)]
            self.auto_refresh_values = ['1', '2', '3', '4', '5', '6']

            self.headers = {
                "Item ID": "Item ID",
                "Item Name": "Item Name",
                "Status": "Status",
                "Condition": "Condition"
            }

        elif self.language_code == 'es':
            self.inventory_button_text = 'Inventario'
            self.add_device_button_text = 'Agregar Dispositivo'
            self.settings_button_text = 'Configuración'

            self.inventory_page_title = 'Lista de Inventario'
            self.add_device_page_title = 'Ingresar Nueva Información del Dispositivo'
            self.settings_page_title = 'Configuración'
            self.details_page_title = 'Detalles para el ID de Artículo: {}'

            self.refresh_button_text = 'Actualizar Inventario'
            self.submit_button_text = 'Enviar'
            self.back_to_inventory_text = 'Volver al Inventario'
            self.back_button_text = 'Atrás'
            self.save_settings_text = 'Guardar Configuración'
            self.settings_saved_text = 'Configuración Guardada Exitosamente'
            self.device_added_text = 'Dispositivo Agregado Exitosamente'
            self.no_inventory_text = 'No hay datos de inventario disponibles.'

            self.enable_light_mode_text = 'Activar Modo Claro:'
            self.change_font_size_text = 'Cambiar Tamaño de Fuente:'
            self.clear_cached_data_text = 'Borrar Datos en Caché:'
            self.language_selection_text = 'Selección de Idioma:'
            self.auto_refresh_interval_text = 'Intervalo de Auto-Actualización (horas):'
            self.enable_auto_refresh_text = 'Activar Auto-Actualización:'
            self.clear_cache_button_text = 'Borrar Caché'

            self.form_labels = {
                "Item Name:": "Nombre del Artículo:",
                "Brand/Manufacturer:": "Marca/Fabricante:",
                "Model Number:": "Número de Modelo:",
                "Serial Number:": "Número de Serie:",
                "Purchase Date (YYYY-MM-DD):": "Fecha de Compra (YYYY-MM-DD):",
                "Warranty Expiry (YYYY-MM-DD):": "Vencimiento de Garantía (YYYY-MM-DD):",
                "Status:": "Estado:",
                "Condition:": "Condición:",
                "Assigned To:": "Asignado A:",
                "Location:": "Ubicación:",
                "Value (USD):": "Valor (USD):",
                "Hardware Notes/Specifications:": "Notas/Especificaciones de Hardware:",
                "Disposition:": "Disposición:",
                "Hardware Type:": "Tipo de Hardware:",
                "Tech. Support:": "Soporte Técnico:",
                "Website:": "Sitio Web:",
                "Images URL:": "URL de Imágenes:"
            }

            self.status_values = ['No en Uso', 'En Uso']
            self.condition_values = ['Desconocido', 'Buena Condición', 'Dañado']
            self.disposition_values = ['Mantener', 'Rescatar', 'Reciclar', 'Basura']
            self.hardware_type_values = ['Impresora', 'Escáner', 'Portátil', 'Teléfono', 'Escritorio', 'Tableta', 'Servidor', 'Equipo de Red', 'Otro']
            self.font_size_options = [('Pequeño', 12), ('Mediano', 16), ('Grande', 20)]
            self.auto_refresh_values = ['1', '2', '3', '4', '5', '6']

            self.headers = {
                "Item ID": "ID de Artículo",
                "Item Name": "Nombre del Artículo",
                "Status": "Estado",
                "Condition": "Condición"
            }

    def get_language_display_name(self, code):
        for option in self.language_options:
            if option['code'] == code:
                return option[f'name_{self.language_code}']
        return code

    def on_language_change(self, spinner, text):
        for option in self.language_options:
            if text == option['name_en'] or text == option['name_es']:
                self.language_code = option['code']
                break
        self.init_text_variables()
        self.show_settings_page()

    def clear_content(self):
        self.content_area.clear_widgets()

    def show_inventory_page(self, instance=None):
        self.clear_content()
        self.inventory_data_cache = None

        self.inventory_button.state = 'down'
        self.add_device_button.state = 'normal'
        self.settings_button.state = 'normal'

        self.update_nav_buttons()

        title_label = Label(text=self.inventory_page_title, font_size=self.font_size + 8, size_hint_y=None, height=40, color=self.theme_manager.text_color)
        self.content_area.add_widget(title_label)

        scroll_view = ScrollView(size_hint=(1, 1))

        grid_layout = GridLayout(cols=4, spacing=0, padding=0, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        headers = [self.headers["Item ID"], self.headers["Item Name"], self.headers["Status"], self.headers["Condition"]]
        for index, header in enumerate(headers):
            if index == 0:
                size_hint_x = 0.1
            elif index == 1:
                size_hint_x = 0.5
            else:
                size_hint_x = 0.2
            grid_layout.add_widget(BorderedLabel(
                text=header,
                bold=True,
                font_size=self.font_size,
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=40,
                size_hint_x=size_hint_x,
                color=self.theme_manager.text_color,
                shorten=True,
                shorten_from='right',
                theme_manager=self.theme_manager
            ))

        if not self.inventory_data_cache:
            self.inventory_data_cache = get_inventory_data()
        if not self.inventory_data_cache:
            self.content_area.add_widget(Label(text=self.no_inventory_text, color=self.theme_manager.text_color))
        else:
            for item in self.inventory_data_cache:
                btn = BorderedButton(
                    text=str(item['Item ID']),
                    size_hint_y=None,
                    height=40,
                    size_hint_x=0.1,
                    halign='center',
                    valign='middle',
                    font_size=self.font_size,
                    color=self.theme_manager.text_color,
                    background_normal='',
                    background_color=(0, 0.5, 0, 1),
                    shorten=True,
                    shorten_from='right',
                    theme_manager=self.theme_manager
                )
                btn.bind(on_press=self.create_item_callback(item))
                grid_layout.add_widget(btn)

                grid_layout.add_widget(BorderedLabel(
                    text=item['Item Name'],
                    size_hint_y=None,
                    height=40,
                    size_hint_x=0.5,
                    halign='left',
                    valign='middle',
                    font_size=self.font_size,
                    color=self.theme_manager.text_color,
                    shorten=True,
                    shorten_from='right',
                    theme_manager=self.theme_manager
                ))

                grid_layout.add_widget(BorderedLabel(
                    text=item['Status'],
                    size_hint_y=None,
                    height=40,
                    size_hint_x=0.2,
                    halign='left',
                    valign='middle',
                    font_size=self.font_size,
                    color=self.theme_manager.text_color,
                    shorten=True,
                    shorten_from='right',
                    theme_manager=self.theme_manager
                ))

                grid_layout.add_widget(BorderedLabel(
                    text=item['Condition'],
                    size_hint_y=None,
                    height=40,
                    size_hint_x=0.2,
                    halign='left',
                    valign='middle',
                    font_size=self.font_size,
                    color=self.theme_manager.text_color,
                    shorten=True,
                    shorten_from='right',
                    theme_manager=self.theme_manager
                ))

        scroll_view.add_widget(grid_layout)
        self.content_area.add_widget(scroll_view)

        refresh_button = Button(text=self.refresh_button_text, on_press=self.refresh_inventory, size_hint_y=None, height=50, font_size=self.font_size)
        refresh_button.color = self.theme_manager.text_color
        self.content_area.add_widget(refresh_button)

    def update_nav_buttons(self):
        self.inventory_button.text = self.inventory_button_text
        self.add_device_button.text = self.add_device_button_text
        self.settings_button.text = self.settings_button_text
        self.inventory_button.color = self.theme_manager.text_color
        self.add_device_button.color = self.theme_manager.text_color
        self.settings_button.color = self.theme_manager.text_color

    def create_item_callback(self, item):
        return lambda instance: self.view_item_details(item)

    def refresh_inventory(self, instance=None):
        self.inventory_data_cache = get_inventory_data()
        self.show_inventory_page()

    def view_item_details(self, item):
        self.clear_content()

        self.inventory_button.state = 'down'
        self.add_device_button.state = 'normal'
        self.settings_button.state = 'normal'

        self.update_nav_buttons()

        title_text = self.details_page_title.format(item['Item ID'])
        title_label = Label(text=title_text, font_size=self.font_size + 8, size_hint_y=None, height=40, color=self.theme_manager.text_color)
        self.content_area.add_widget(title_label)

        scroll_view = ScrollView(size_hint=(1, 1))

        details_layout = GridLayout(cols=2, spacing=10, padding=20, size_hint_y=None)
        details_layout.bind(minimum_height=details_layout.setter('height'))

        fields = {
            'Item ID': item.get('Item ID', 'N/A'),
            'Item Name': item.get('Item Name', 'N/A'),
            'Brand/Manufacturer': item.get('Brand/Manufacturer', 'N/A'),
            'Model Number': item.get('Model Number', 'N/A'),
            'Serial Number': item.get('Serial Number', 'N/A'),
            'Purchase Date': item.get('Purchase Date', 'N/A'),
            'Warranty Expiry': item.get('Warranty Expiry', 'N/A'),
            'Status': item.get('Status', 'N/A'),
            'Condition': item.get('Condition', 'N/A'),
            'Assigned To': item.get('Assigned To', 'N/A'),
            'Location': item.get('Location', 'N/A'),
            'Value': item.get('Value', 'N/A'),
            'Hardware Notes/Specifications': item.get('Hardware Notes/Specifications', 'N/A'),
            'Disposition': item.get('Disposition', 'N/A'),
            'Log Date': item.get('Log Date', 'N/A'),
            'Hardware Type': item.get('Hardware Type', 'N/A'),
            'Tech. Support': item.get('Tech. Support', 'N/A'),
            'Website': item.get('Website', 'N/A'),
            'Images': item.get('Images', 'N/A')
        }

        for field, value in fields.items():
            details_layout.add_widget(Label(
                text=f"{field}:",
                bold=True,
                font_size=self.font_size,
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=40,
                text_size=(dp(150), None),
                color=self.theme_manager.text_color,
            ))

            if field in ['Website', 'Images'] and value != 'N/A':
                link_label = Label(
                    text=f"[ref={value}][u]{value}[/u][/ref]",
                    markup=True,
                    font_size=self.font_size,
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=40,
                    color=(0, 0, 1, 1) if self.theme_manager.is_light_mode else (0, 0.7, 1, 1),
                )
                link_label.bind(on_ref_press=self.open_link)
                details_layout.add_widget(link_label)
            else:
                details_layout.add_widget(Label(
                    text=str(value),
                    font_size=self.font_size,
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=40,
                    text_size=(dp(200), None),
                    color=self.theme_manager.text_color,
                ))

        scroll_view.add_widget(details_layout)
        self.content_area.add_widget(scroll_view)

        back_button = Button(text=self.back_to_inventory_text, on_press=self.show_inventory_page, size_hint_y=None, height=50, font_size=self.font_size)
        back_button.color = self.theme_manager.text_color
        self.content_area.add_widget(back_button)

    def open_link(self, instance, ref):
        webbrowser.open(ref)

    def show_add_device_page(self, instance=None):
        self.clear_content()

        self.inventory_button.state = 'normal'
        self.add_device_button.state = 'down'
        self.settings_button.state = 'normal'

        self.update_nav_buttons()

        title_label = Label(text=self.add_device_page_title, font_size=self.font_size + 8, size_hint_y=None, height=40,
                            color=self.theme_manager.text_color)
        self.content_area.add_widget(title_label)

        form_scroll = ScrollView(size_hint=(1, 1))

        form_layout = GridLayout(cols=2, spacing=10, padding=20, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        def add_form_row(label_text, widget):
            label = Label(text=label_text, color=self.theme_manager.text_color, size_hint_y=None, height=40, font_size=self.font_size)
            form_layout.add_widget(label)
            widget.size_hint_y = None
            widget.height = 40
            widget.font_size = self.font_size
            form_layout.add_widget(widget)

        self.item_name_input = TextInput(hint_text=self.form_labels["Item Name:"], multiline=False)
        add_form_row(self.form_labels["Item Name:"], self.item_name_input)

        self.brand_input = TextInput(hint_text=self.form_labels["Brand/Manufacturer:"], multiline=False)
        add_form_row(self.form_labels["Brand/Manufacturer:"], self.brand_input)

        self.model_number_input = TextInput(hint_text=self.form_labels["Model Number:"], multiline=False)
        add_form_row(self.form_labels["Model Number:"], self.model_number_input)

        self.serial_number_input = TextInput(hint_text=self.form_labels["Serial Number:"], multiline=False)
        add_form_row(self.form_labels["Serial Number:"], self.serial_number_input)

        self.purchase_date_input = TextInput(hint_text="YYYY-MM-DD", multiline=False)
        add_form_row(self.form_labels["Purchase Date (YYYY-MM-DD):"], self.purchase_date_input)

        self.warranty_expiry_input = TextInput(hint_text="YYYY-MM-DD", multiline=False)
        add_form_row(self.form_labels["Warranty Expiry (YYYY-MM-DD):"], self.warranty_expiry_input)

        self.status_spinner = Spinner(
            text=self.status_values[0],
            values=self.status_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        add_form_row(self.form_labels["Status:"], self.status_spinner)

        self.condition_spinner = Spinner(
            text=self.condition_values[0],
            values=self.condition_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        add_form_row(self.form_labels["Condition:"], self.condition_spinner)

        self.assigned_to_input = TextInput(hint_text=self.form_labels["Assigned To:"], multiline=False)
        add_form_row(self.form_labels["Assigned To:"], self.assigned_to_input)

        self.location_input = TextInput(hint_text=self.form_labels["Location:"], multiline=False)
        add_form_row(self.form_labels["Location:"], self.location_input)

        self.value_input = TextInput(hint_text=self.form_labels["Value (USD):"], multiline=False, input_filter='float')
        add_form_row(self.form_labels["Value (USD):"], self.value_input)

        self.notes_input = TextInput(hint_text=self.form_labels["Hardware Notes/Specifications:"], multiline=True)
        self.notes_input.size_hint_y = None
        self.notes_input.height = 100
        self.notes_input.font_size = self.font_size
        label = Label(text=self.form_labels["Hardware Notes/Specifications:"], color=self.theme_manager.text_color, size_hint_y=None, height=100, font_size=self.font_size)
        form_layout.add_widget(label)
        form_layout.add_widget(self.notes_input)

        self.disposition_spinner = Spinner(
            text=self.disposition_values[0],
            values=self.disposition_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        add_form_row(self.form_labels["Disposition:"], self.disposition_spinner)

        self.hardware_type_spinner = Spinner(
            text=self.hardware_type_values[0],
            values=self.hardware_type_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        add_form_row(self.form_labels["Hardware Type:"], self.hardware_type_spinner)

        self.tech_support_input = TextInput(hint_text=self.form_labels["Tech. Support:"], multiline=False)
        add_form_row(self.form_labels["Tech. Support:"], self.tech_support_input)

        self.website_input = TextInput(hint_text=self.form_labels["Website:"], multiline=False)
        add_form_row(self.form_labels["Website:"], self.website_input)

        self.images_input = TextInput(hint_text=self.form_labels["Images URL:"], multiline=False)
        add_form_row(self.form_labels["Images URL:"], self.images_input)

        form_scroll.add_widget(form_layout)
        self.content_area.add_widget(form_scroll)

        self.submit_button = Button(text=self.submit_button_text, on_press=self.submit_new_device, size_hint_y=None, height=50, font_size=self.font_size)
        self.submit_button.color = self.theme_manager.text_color
        self.content_area.add_widget(self.submit_button)

    def submit_new_device(self, instance):
        item_name = self.item_name_input.text
        brand = self.brand_input.text
        model_number = self.model_number_input.text
        serial_number = self.serial_number_input.text
        purchase_date = self.purchase_date_input.text
        warranty_expiry = self.warranty_expiry_input.text
        status = self.status_spinner.text
        condition = self.condition_spinner.text
        assigned_to = self.assigned_to_input.text
        location = self.location_input.text
        value = self.value_input.text
        notes = self.notes_input.text
        disposition = self.disposition_spinner.text
        hardware_type = self.hardware_type_spinner.text
        tech_support = self.tech_support_input.text
        website = self.website_input.text
        images = self.images_input.text

        item_id = ''.join(random.sample(string.ascii_uppercase + string.digits, 5))

        try:
            add_device(
                item_id,
                item_name,
                brand,
                model_number,
                serial_number,
                purchase_date,
                warranty_expiry,
                status,
                condition,
                assigned_to,
                location,
                value,
                notes,
                disposition,
                hardware_type,
                tech_support,
                website,
                images
            )
            self.clear_content()
            success_label = Label(text=self.device_added_text, color=self.theme_manager.text_color, font_size=self.font_size)
            self.content_area.add_widget(success_label)
            back_button = Button(text=self.back_to_inventory_text, on_press=self.show_inventory_page, font_size=self.font_size)
            back_button.color = self.theme_manager.text_color
            self.content_area.add_widget(back_button)
        except Exception as e:
            error_label = Label(text=str(e), color=(1, 0, 0, 1), font_size=self.font_size)
            self.content_area.add_widget(error_label)

    def show_settings_page(self, instance=None):
        self.clear_content()

        self.inventory_button.state = 'normal'
        self.add_device_button.state = 'normal'
        self.settings_button.state = 'down'

        self.update_nav_buttons()

        title_label = Label(
            text=self.settings_page_title,
            font_size=self.font_size + 8,
            size_hint_y=None,
            height=40,
            color=self.theme_manager.text_color
        )
        self.content_area.add_widget(title_label)

        settings_scroll = ScrollView(size_hint=(1, 1))

        settings_layout = GridLayout(cols=2, spacing=20, padding=20, size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))

        # Light Mode Switch
        settings_layout.add_widget(Label(
            text=self.enable_light_mode_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        self.light_mode_switch = Switch(active=self.theme_manager.is_light_mode, size_hint_y=None, height=40)
        self.light_mode_switch.bind(active=self.toggle_light_mode)
        settings_layout.add_widget(self.light_mode_switch)

        # Font Size Spinner
        settings_layout.add_widget(Label(
            text=self.change_font_size_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        current_font_size_display_text = ''
        for display_text, size_value in self.font_size_options:
            if size_value == self.font_size:
                current_font_size_display_text = display_text
                break

        self.font_size_spinner = Spinner(
            text=current_font_size_display_text,
            values=[option[0] for option in self.font_size_options],
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        self.font_size_spinner.bind(text=self.on_font_size_change)
        settings_layout.add_widget(self.font_size_spinner)

        # Clear Cache Button
        settings_layout.add_widget(Label(
            text=self.clear_cached_data_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        clear_cache_button = Button(
            text=self.clear_cache_button_text,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        clear_cache_button.bind(on_press=self.clear_cache)
        clear_cache_button.color = self.theme_manager.text_color
        settings_layout.add_widget(clear_cache_button)

        # Language Selection Spinner
        settings_layout.add_widget(Label(
            text=self.language_selection_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        self.language_spinner = Spinner(
            text=self.language,
            values=self.language_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        self.language_spinner.bind(text=self.on_language_change)
        settings_layout.add_widget(self.language_spinner)

        # Auto-Refresh Interval Spinner
        settings_layout.add_widget(Label(
            text=self.auto_refresh_interval_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        self.auto_refresh_spinner = Spinner(
            text=self.auto_refresh_values[1],
            values=self.auto_refresh_values,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        )
        settings_layout.add_widget(self.auto_refresh_spinner)

        # Auto-Refresh Switch
        settings_layout.add_widget(Label(
            text=self.enable_auto_refresh_text,
            color=self.theme_manager.text_color,
            size_hint_y=None,
            height=40,
            font_size=self.font_size
        ))
        self.auto_refresh_switch = Switch(active=False, size_hint_y=None, height=40)
        self.auto_refresh_switch.bind(active=self.toggle_auto_refresh)
        settings_layout.add_widget(self.auto_refresh_switch)

        settings_scroll.add_widget(settings_layout)
        self.content_area.add_widget(settings_scroll)

        save_button = Button(
            text=self.save_settings_text,
            on_press=self.save_settings,
            size_hint_y=None,
            height=50,
            font_size=self.font_size
        )
        save_button.color = self.theme_manager.text_color
        self.content_area.add_widget(save_button)

    def toggle_light_mode(self, instance, value):
        self.theme_manager.toggle_theme(value)
        self.update_theme()
        self.show_settings_page()

    def toggle_auto_refresh(self, instance, value):
        if value:
            interval_hours = int(self.auto_refresh_spinner.text)
            interval_seconds = interval_hours * 3600
            if self.auto_refresh_event:
                self.auto_refresh_event.cancel()
            self.auto_refresh_event = Clock.schedule_interval(self.auto_refresh_inventory, interval_seconds)
        else:
            if self.auto_refresh_event:
                self.auto_refresh_event.cancel()
                self.auto_refresh_event = None

    def auto_refresh_inventory(self, dt):
        self.refresh_inventory()

    def on_font_size_change(self, spinner, text):
        for display_text, size_value in self.font_size_options:
            if display_text == text:
                self.font_size = size_value
                break
        self.show_settings_page()

    def clear_cache(self, instance):
        self.inventory_data_cache = None

    def save_settings(self, instance):
        if self.auto_refresh_switch.active:
            self.toggle_auto_refresh(self.auto_refresh_switch, True)
        else:
            self.toggle_auto_refresh(self.auto_refresh_switch, False)

        self.clear_content()
        success_label = Label(text=self.settings_saved_text, color=self.theme_manager.text_color, font_size=self.font_size)
        self.content_area.add_widget(success_label)
        back_button = Button(text=self.back_button_text, on_press=self.show_settings_page, font_size=self.font_size)
        back_button.color = self.theme_manager.text_color
        self.content_area.add_widget(back_button)

    def update_theme(self):
        Window.clearcolor = self.theme_manager.background_color
        self.inventory_button.color = self.theme_manager.text_color
        self.add_device_button.color = self.theme_manager.text_color
        self.settings_button.color = self.theme_manager.text_color
        for widget in self.content_area.walk():
            if hasattr(widget, 'color'):
                widget.color = self.theme_manager.text_color

class WarehouseApp(App):
    def build(self):
        Config.set('graphics', 'width', '480')
        Config.set('graphics', 'height', '800')
        return HomePage()

    def on_pause(self):
        print("App paused. Saving state and pausing tasks.")
        self.root.clear_content()
        return True

    def on_resume(self):
        print("App resumed. Restoring state and resuming tasks.")
        self.root.show_inventory_page()

    def on_stop(self):
        print("App stopped. Cleaning up resources.")
        if self.root.auto_refresh_event:
            self.root.auto_refresh_event.cancel()
        self.root.inventory_data_cache = None

if __name__ == '__main__':
    WarehouseApp().run()
