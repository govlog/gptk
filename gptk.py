import gi
import openai
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

openai.api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def ask_gpt(question):

    openai_answer=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "Un bot précis/concis" },
                { "role": "user", "content": question }
            ]
    )

    return openai_answer.choices[0].message.content

class TerminalWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self, title="Govlog GPT CLIENT")
        self.set_border_width(10)
        self.set_default_size(600, 400)

        self.set_opacity(0.9)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        scrolledwindow = Gtk.ScrolledWindow()
        vbox.pack_start(scrolledwindow, True, True, 0)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        scrolledwindow.add(self.textview)

        font_desc = "Hack Nerd Font Mono Regular 16"
        self.textview.override_font(Pango.FontDescription(font_desc))

        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        self.tag_green = self.textbuffer.create_tag("green", foreground="green")
        self.tag_blue = self.textbuffer.create_tag("blue", foreground="light blue")
        self.tag_code = self.textbuffer.create_tag("code", foreground="light green")

        self.textview.connect("key-release-event", self.on_key_release)
        self.textview.connect("button-press-event", self.on_button_press)
        self.textview.connect("scroll-event", self.on_scroll)

        self.entry = Gtk.Entry()
        vbox.pack_start(self.entry, False, False, 0)
        self.entry.connect("activate", self.on_entry_activate)

    def on_entry_activate(self, widget):
        question_text = widget.get_text()
        user_name = os.getenv("USER")
        display_text = f"{user_name}> {question_text}\n"
        self.textbuffer.insert(self.textbuffer.get_end_iter(), display_text)
        response = "\n" + ask_gpt(question_text) + "\n"
        self.display_response(response)
        widget.set_text("")

    def on_key_release(self, widget, event):
        if event.keyval == Gdk.KEY_Return and event.state & Gdk.ModifierType.CONTROL_MASK:
            start_iter = self.textbuffer.get_start_iter()
            end_iter = self.textbuffer.get_end_iter()
            text = self.textbuffer.get_text(start_iter, end_iter, False)
            lines = text.split("\n")
            last_line = lines[-2] if len(lines) > 1 else lines[-1]
            response = "\n" + ask_gpt(last_line) + '\n'
            self.display_response(response)        
            
    def on_button_press(self, widget, event):
        if event.button == 3:  # Right click
            menu = Gtk.Menu()

            copy_item = Gtk.MenuItem.new_with_label("Copier")
            copy_item.connect("activate", self.copy_text)
            menu.append(copy_item)

            paste_item = Gtk.MenuItem.new_with_label("Coller")
            paste_item.connect("activate", self.paste_text)
            menu.append(paste_item)

            clear_item = Gtk.MenuItem.new_with_label("Clear conversation")
            clear_item.connect("activate", self.clear_conversation)
            menu.append(clear_item)

            menu.show_all()
            menu.popup_at_pointer(None)

    def copy_text(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.copy_clipboard(clipboard)

    def paste_text(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.paste_clipboard(clipboard, None, self.textview.get_editable())

    def clear_conversation(self, widget):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.delete(start_iter, end_iter)


    def on_scroll(self, widget, event):
        """ handles on scroll event"""

        # Handles zoom in / zoom out on Ctrl+mouse wheel
        accel_mask = Gtk.accelerator_get_default_mod_mask()
        if event.state & accel_mask == Gdk.ModifierType.CONTROL_MASK:

            font_desc = self.textview.get_pango_context().get_font_description()
            font_size = font_desc.get_size() / Pango.SCALE

            direction = event.get_scroll_deltas()[2]
            if direction > 0:  # scrolling down -> zoom out
                font_size -= 2
            else:
                font_size += 2

            font_desc.set_size(font_size * Pango.SCALE)
            self.textview.override_font(font_desc)

    def display_response(self, response_text):
        end_iter = self.textbuffer.get_end_iter()

        if "```" in response_text:
            parts = response_text.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    self.textbuffer.insert_with_tags(end_iter, part, self.tag_blue)
                else:
                    self.textbuffer.insert_with_tags(end_iter, part, self.tag_code)
        else:
            self.textbuffer.insert_with_tags(end_iter, response_text, self.tag_blue)

        self.textbuffer.insert(end_iter, "\n")

def main():
    win = TerminalWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

