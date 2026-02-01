import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math


class ModernButton(tk.Canvas):
    """Custom button with hover effects and gradients"""
    def __init__(self, parent, text, command, bg_color, hover_color, **kwargs):
        self.width = kwargs.get('width', 280)
        self.height = kwargs.get('height', 80)
        super().__init__(parent, width=self.width, height=self.height, 
                        highlightthickness=0, bg=kwargs.get('parent_bg', '#0a0e27'))
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        
        self.draw_button()
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def draw_button(self):
        self.delete('all')
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Shadow
        shadow_offset = 0 if self.is_hovered else 4
        self.create_rectangle(5, 5 + shadow_offset, self.width - 5, self.height - 5 + shadow_offset,
                            fill='#000000', outline='', tags='shadow')
        
        # Button background with rounded corners effect
        self.create_rectangle(0, shadow_offset, self.width - 10, self.height - 10 + shadow_offset,
                            fill=color, outline='', tags='bg')
        
        # Shine effect
        self.create_rectangle(5, 5 + shadow_offset, self.width - 15, 25 + shadow_offset,
                            fill='#ffffff', outline='', stipple='gray25', tags='shine')
        
        # Text
        self.create_text(self.width // 2 - 5, self.height // 2 - 5 + shadow_offset,
                        text=self.text, fill='white', 
                        font=('Segoe UI', 14, 'bold'), tags='text')
    
    def on_enter(self, e):
        self.is_hovered = True
        self.draw_button()
        self.config(cursor='hand2')
        
    def on_leave(self, e):
        self.is_hovered = False
        self.draw_button()
        self.config(cursor='')
        
    def on_click(self, e):
        if self.command:
            self.command()


class ModernEntry(tk.Frame):
    """Custom entry with floating label"""
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, bg='#0a0e27')
        self.label_text = label_text
        
        # Container for the entry with gradient-like border
        self.border_frame = tk.Frame(self, bg='#2d4a7c', bd=0)
        self.border_frame.pack(fill=tk.BOTH, padx=2, pady=2)
        
        # Label
        self.label = tk.Label(self.border_frame, text=label_text, 
                             font=('Segoe UI', 9), bg='#0a0e27', fg='#7e9bc9')
        self.label.pack(anchor=tk.W, padx=10, pady=(8, 0))
        
        # Entry
        self.entry = tk.Entry(self.border_frame, font=('Segoe UI', 11), 
                             bg='#0a0e27', fg='#ffffff', 
                             insertbackground='#4a9eff', bd=0,
                             relief=tk.FLAT)
        self.entry.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Bind focus events for animation
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        
    def on_focus_in(self, e):
        self.border_frame.config(bg='#4a9eff')
        self.label.config(fg='#4a9eff')
        
    def on_focus_out(self, e):
        self.border_frame.config(bg='#2d4a7c')
        self.label.config(fg='#7e9bc9')
        
    def get(self):
        return self.entry.get()
    
    def insert(self, index, text):
        self.entry.insert(index, text)


class ModernTextArea(tk.Frame):
    """Custom text area with floating label"""
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, bg='#0a0e27')
        self.label_text = label_text
        
        # Container
        self.border_frame = tk.Frame(self, bg='#2d4a7c', bd=0)
        self.border_frame.pack(fill=tk.BOTH, padx=2, pady=2)
        
        # Label
        self.label = tk.Label(self.border_frame, text=label_text, 
                             font=('Segoe UI', 9), bg='#0a0e27', fg='#7e9bc9')
        self.label.pack(anchor=tk.W, padx=10, pady=(8, 0))
        
        # Text widget
        self.text = tk.Text(self.border_frame, font=('Segoe UI', 10), 
                           bg='#0a0e27', fg='#ffffff', 
                           insertbackground='#4a9eff', bd=0,
                           relief=tk.FLAT, height=4, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, padx=10, pady=(0, 8))
        
        # Bind focus events
        self.text.bind('<FocusIn>', self.on_focus_in)
        self.text.bind('<FocusOut>', self.on_focus_out)
        
    def on_focus_in(self, e):
        self.border_frame.config(bg='#4a9eff')
        self.label.config(fg='#4a9eff')
        
    def on_focus_out(self, e):
        self.border_frame.config(bg='#2d4a7c')
        self.label.config(fg='#7e9bc9')
        
    def get(self, start, end):
        return self.text.get(start, end)


class AnimatedBackground(tk.Canvas):
    """Animated gradient background"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.colors = ['#0a0e27', '#1a1e47', '#0a0e27']
        self.current_color_index = 0
        self.animation_step = 0
        
    def animate(self):
        # Create subtle color shift animation
        self.animation_step = (self.animation_step + 1) % 100
        
        # Draw gradient background
        self.delete('all')
        height = self.winfo_height()
        width = self.winfo_width()
        
        if height > 1 and width > 1:
            # Create vertical gradient
            for i in range(height):
                ratio = i / height
                # Interpolate between dark blues
                r = int(10 + ratio * 10)
                g = int(14 + ratio * 16)
                b = int(39 + ratio * 32)
                color = f'#{r:02x}{g:02x}{b:02x}'
                self.create_line(0, i, width, i, fill=color, tags='gradient')
            
            # Add some subtle animated particles
            for j in range(15):
                offset = (self.animation_step + j * 7) % 100
                x = (width * j / 15 + offset * 2) % width
                y = (height * ((j * 17) % 100) / 100)
                size = 2 + (j % 3)
                opacity = ['#4a9eff', '#7e9bc9', '#2d4a7c'][j % 3]
                self.create_oval(x, y, x + size, y + size, 
                               fill=opacity, outline='', tags='particle')
        
        self.after(50, self.animate)


class DeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Logistyczny Pro")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#0a0e27')
        
        # Center window
        self.center_window()
        
        # Create animated background
        self.bg_canvas = AnimatedBackground(self.root, bg='#0a0e27')
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Start animation
        self.root.after(100, lambda: self.bg_canvas.animate())
        
        # Show main menu
        self.show_main_menu()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def clear_content(self):
        """Clear content while keeping background"""
        for widget in self.root.winfo_children():
            if widget != self.bg_canvas:
                widget.destroy()
    
    def show_main_menu(self):
        """Display main menu with modern design"""
        self.clear_content()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0e27')
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title with glow effect
        title_canvas = tk.Canvas(main_frame, width=500, height=120, 
                                bg='#0a0e27', highlightthickness=0)
        title_canvas.pack(pady=(0, 30))
        
        # Glow effect
        for offset in range(8, 0, -2):
            title_canvas.create_text(250, 40, text='SYSTEM',
                                    font=('Segoe UI', 42, 'bold'),
                                    fill=f'#1a4d{offset*2+100:02x}', tags='glow')
        
        # Main title
        title_canvas.create_text(250, 40, text='SYSTEM',
                                font=('Segoe UI', 42, 'bold'),
                                fill='#4a9eff', tags='title')
        
        # Subtitle
        title_canvas.create_text(250, 85, text='LOGISTYCZNY PRO',
                                font=('Segoe UI', 18),
                                fill='#7e9bc9', tags='subtitle')
        
        # Instruction text
        instruction = tk.Label(main_frame, text='Wybierz operację',
                             font=('Segoe UI', 12), fg='#7e9bc9', bg='#0a0e27')
        instruction.pack(pady=(0, 30))
        
        # Buttons container
        buttons_frame = tk.Frame(main_frame, bg='#0a0e27')
        buttons_frame.pack()
        
        # Delivery button
        delivery_btn = ModernButton(
            buttons_frame, 
            '📦  NOWA DOSTAWA',
            self.create_delivery,
            bg_color='#2563eb',
            hover_color='#3b82f6',
            parent_bg='#0a0e27'
        )
        delivery_btn.pack(pady=10)
        
        # Transfer button
        transfer_btn = ModernButton(
            buttons_frame,
            '🚚  ZLECENIE PRZENIESIENIA', 
            self.create_transfer,
            bg_color='#7c3aed',
            hover_color='#8b5cf6',
            parent_bg='#0a0e27'
        )
        transfer_btn.pack(pady=10)
        
        # Footer
        footer = tk.Label(self.root, 
                         text=f'v2.0 • {datetime.now().strftime("%Y")} • System Logistyczny',
                         font=('Segoe UI', 8), fg='#4a5568', bg='#0a0e27')
        footer.pack(side=tk.BOTTOM, pady=10)
    
    def create_delivery(self):
        """Form for creating delivery"""
        self.clear_content()
        
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#0a0e27')
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Header
        header_canvas = tk.Canvas(main_frame, width=600, height=80,
                                 bg='#0a0e27', highlightthickness=0)
        header_canvas.pack(pady=(0, 20))
        
        # Header glow
        for offset in range(6, 0, -2):
            header_canvas.create_text(300, 40, text='📦 NOWA DOSTAWA',
                                     font=('Segoe UI', 28, 'bold'),
                                     fill=f'#1a4d{offset*2+100:02x}')
        
        header_canvas.create_text(300, 40, text='📦 NOWA DOSTAWA',
                                 font=('Segoe UI', 28, 'bold'),
                                 fill='#4a9eff')
        
        # Form
        form_frame = tk.Frame(main_frame, bg='#0a0e27')
        form_frame.pack(pady=10)
        
        # Form fields
        delivery_number = ModernEntry(form_frame, 'Numer dostawy')
        delivery_number.pack(fill=tk.X, pady=8)
        
        supplier = ModernEntry(form_frame, 'Dostawca')
        supplier.pack(fill=tk.X, pady=8)
        
        delivery_date = ModernEntry(form_frame, 'Data dostawy')
        delivery_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        delivery_date.pack(fill=tk.X, pady=8)
        
        notes = ModernTextArea(form_frame, 'Uwagi')
        notes.pack(fill=tk.X, pady=8)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#0a0e27')
        button_frame.pack(pady=20)
        
        save_btn = ModernButton(
            button_frame,
            '✓  ZAPISZ',
            lambda: self.save_delivery(
                delivery_number.get(), 
                supplier.get(), 
                delivery_date.get(), 
                notes.get("1.0", tk.END)
            ),
            bg_color='#059669',
            hover_color='#10b981',
            width=130,
            height=50,
            parent_bg='#0a0e27'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = ModernButton(
            button_frame,
            '←  POWRÓT',
            self.show_main_menu,
            bg_color='#64748b',
            hover_color='#94a3b8',
            width=130,
            height=50,
            parent_bg='#0a0e27'
        )
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def create_transfer(self):
        """Form for creating transfer order"""
        self.clear_content()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0e27')
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Header
        header_canvas = tk.Canvas(main_frame, width=600, height=80,
                                 bg='#0a0e27', highlightthickness=0)
        header_canvas.pack(pady=(0, 20))
        
        # Header glow
        for offset in range(6, 0, -2):
            header_canvas.create_text(300, 40, text='🚚 ZLECENIE PRZENIESIENIA',
                                     font=('Segoe UI', 26, 'bold'),
                                     fill=f'#{offset*2+100:02x}1a4d')
        
        header_canvas.create_text(300, 40, text='🚚 ZLECENIE PRZENIESIENIA',
                                 font=('Segoe UI', 26, 'bold'),
                                 fill='#8b5cf6')
        
        # Form
        form_frame = tk.Frame(main_frame, bg='#0a0e27')
        form_frame.pack(pady=10)
        
        # Form fields
        transfer_number = ModernEntry(form_frame, 'Numer zlecenia')
        transfer_number.pack(fill=tk.X, pady=8)
        
        from_location = ModernEntry(form_frame, 'Z lokalizacji')
        from_location.pack(fill=tk.X, pady=8)
        
        to_location = ModernEntry(form_frame, 'Do lokalizacji')
        to_location.pack(fill=tk.X, pady=8)
        
        transfer_date = ModernEntry(form_frame, 'Data przeniesienia')
        transfer_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        transfer_date.pack(fill=tk.X, pady=8)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#0a0e27')
        button_frame.pack(pady=20)
        
        save_btn = ModernButton(
            button_frame,
            '✓  ZAPISZ',
            lambda: self.save_transfer(
                transfer_number.get(),
                from_location.get(),
                to_location.get(),
                transfer_date.get()
            ),
            bg_color='#059669',
            hover_color='#10b981',
            width=130,
            height=50,
            parent_bg='#0a0e27'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = ModernButton(
            button_frame,
            '←  POWRÓT',
            self.show_main_menu,
            bg_color='#64748b',
            hover_color='#94a3b8',
            width=130,
            height=50,
            parent_bg='#0a0e27'
        )
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def save_delivery(self, number, supplier, date, notes):
        """Save delivery"""
        if not number or not supplier:
            messagebox.showerror("Błąd", "Wypełnij wszystkie wymagane pola!")
            return
        
        messagebox.showinfo(
            "Sukces",
            f"✓ Dostawa została utworzona!\n\n"
            f"Numer: {number}\n"
            f"Dostawca: {supplier}\n"
            f"Data: {date}"
        )
        self.show_main_menu()
    
    def save_transfer(self, number, from_loc, to_loc, date):
        """Save transfer order"""
        if not number or not from_loc or not to_loc:
            messagebox.showerror("Błąd", "Wypełnij wszystkie wymagane pola!")
            return
        
        messagebox.showinfo(
            "Sukces",
            f"✓ Zlecenie przeniesienia zostało utworzone!\n\n"
            f"Numer: {number}\n"
            f"Z: {from_loc}\n"
            f"Do: {to_loc}\n"
            f"Data: {date}"
        )
        self.show_main_menu()


def main():
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()