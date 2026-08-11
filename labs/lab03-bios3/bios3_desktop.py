"""
БИОС-3: Космическая экосистема — ВЕРСИЯ 3.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import math


class SpaceEcosystemGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Космическая Экосистема БИОС-3 — Научный симулятор")
        self.root.geometry("1400x850")
        self.root.configure(bg='#0a0a2a')

        # Флаг завершения игры
        self.game_over = False

        self.root.option_add('*Font', 'SegoeUI 10')

        self.COLORS = {
            'bg_primary': '#0a0a2a',
            'bg_secondary': '#1a1a3a',
            'bg_card': '#2a2a5a',
            'accent_blue': '#00a8ff',
            'accent_green': '#00d2b8',
            'accent_purple': '#9c88ff',
            'accent_orange': '#ff9f43',
            'accent_red': '#ff6b6b',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a8ff',
            'success': '#00d2b8',
            'warning': '#ff9f43',
            'danger': '#ff6b6b'
        }

        # Научные константы (реальные данные из БИОС-3, скорректированные)
        self.SCIENTIFIC_CONSTANTS = {
            'photosynthesis_rate': 0.45,   # кг O₂/(кг·день) × 0.1 = 0.045 эфф. (FIX-2)
            'human_oxygen_consumption': 0.84,
            'human_water_consumption': 2.5,
            'human_food_consumption': 0.8,
            'plant_transpiration_rate': 0.08,  # л воды / кг биомассы / день (FIX-1)
            'co2_assimilation': 1.375,   # стехиометрия 44/32 (уточнено)
            'co2_respiration_ratio': 1.375,  # FIX-4: для дыхания растений
            'energy_per_sqm': 0.2,
            'waste_recycling_efficiency': 0.85,
            'plant_growth_rate': 0.05
        }

        self.day = 0
        self.max_days = 14
        self.crew_members = 3

        # ── ИСПРАВЛЕНИЕ 1: снижены начальные запасы ──────────────────────────
        # Расчёт: еда 25 кг / 2.4 кг·день⁻¹ ≈ 10 дней → игрок обязан собрать урожай
        # Вода 280 л / ~32 л·день⁻¹ ≈ 8.7 дней → игрок обязан запустить рециркуляцию
        # Энергия 150 кВт·ч / ~12.5 кВт·ч·день⁻¹ ≈ 12 дней → нужна экономия
        self.oxygen_kg = 200      # кг кислорода (было 200 — оставляем)
        self.water_liters = 280   # л (было 500)
        self.food_kg = 25         # кг (было 50)
        self.plant_biomass_kg = 100
        self.co2_kg = 50
        self.waste_kg = 0
        self.energy_kwh = 150     # кВт·ч (было 200)
        self.crew_happiness = 100

        # Физические параметры станции
        self.grow_area = 50
        self.water_recycler_efficiency = 0.75
        self.air_filter_efficiency = 0.80

        # ── ИСПРАВЛЕНИЕ 2: система деградации ────────────────────────────────
        # Если игрок не выполняет эксперименты, системы деградируют.
        # photosynthesis_modifier: умножается на o2_produced каждый день.
        #   При бездействии -0.06/день → за 5 дней 0.7, за 10 дней 0.4 → кислород тает.
        # filter_modifier: умножается на эффективность фильтра.
        #   При бездействии -0.05/день → СО₂ накапливается.
        self.photosynthesis_modifier = 1.0   # [0.3 … 1.0]
        self.filter_modifier = 1.0            # [0.3 … 1.0]
        self.actions_taken_today = 0          # сбрасывается каждый день
        self.max_actions_per_day = 3          # FIX-6: лимит действий в день
        self.solar_cooldown = 0               # FIX-5: кулдаун солнечных панелей

        # История для графиков
        self.history = {
            'days': [0],
            'oxygen': [self.oxygen_kg],
            'water': [self.water_liters],
            'food': [self.food_kg],
            'plant_biomass': [self.plant_biomass_kg],
            'co2': [self.co2_kg],
            'energy': [self.energy_kwh],
            'happiness': [self.crew_happiness],
            'waste': [self.waste_kg]
        }

        self.science_facts = [
            "🌿 БИОС-3 был советским экспериментом по созданию замкнутой экосистемы (1972–1984)",
            "💡 Растения производят кислород через фотосинтез: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
            "🔄 В БИОС-3 достигалось 85% рециркуляции воды и 100% регенерации воздуха",
            "👨‍🚀 Один человек потребляет ~0.84 кг кислорода и производит ~1.0 кг CO₂ в сутки",
            "🌾 Пшеница на 1 м² производит ~15 г кислорода и потребляет ~22 г CO₂ в день",
            "💧 Система рециркуляции имитирует природный круговорот воды: испарение → конденсация",
            "⚖️ Баланс O₂/CO₂ критичен: при 1% CO₂ у людей начинается головная боль",
            "🔬 Хлорелла — идеальная космическая культура: быстро растёт и эффективно фотосинтезирует",
            "🛠️ Регулярное обслуживание систем — ключ к выживанию. Без него КПД падает каждый день!"
        ]

        self.current_fact = 0
        self.research_points = 0
        self.discoveries = []

        self.next_day_btn = None
        self.experiment_buttons = []

        self.create_styles()
        self.setup_ui()
        self.update_display()
        self.show_science_tip()

    # ─────────────────────────────────────────────────────────────────────────
    def create_styles(self):
        style = ttk.Style()
        style.configure('Modern.TButton', font=('SegoeUI', 10, 'bold'),
                        borderwidth=0, focuscolor='none', relief='flat')
        style.map('Modern.TButton',
                  background=[('active', self.COLORS['accent_blue']),
                              ('!disabled', self.COLORS['accent_purple'])],
                  foreground=[('!disabled', 'white')])

    # ─────────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg=self.COLORS['bg_primary'])
        title_frame.pack(pady=10)
        title_container = tk.Frame(title_frame, bg=self.COLORS['bg_primary'])
        title_container.pack()

        tk.Label(title_container,
                 text="🚀 БИОС-3: НАУЧНЫЙ СИМУЛЯТОР КОСМИЧЕСКОЙ ЭКОСИСТЕМЫ",
                 font=('SegoeUI', 20, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_primary']).pack()

        tk.Label(title_container,
                 text="▸ Эксперимент по созданию замкнутой биологической системы жизнеобеспечения",
                 font=('SegoeUI', 12),
                 fg=self.COLORS['accent_green'],
                 bg=self.COLORS['bg_primary']).pack(pady=(5, 0))

        self.setup_top_indicators()

        main_container = tk.Frame(self.root, bg=self.COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        left_column = tk.Frame(main_container, bg=self.COLORS['bg_primary'])
        left_column.pack(side='left', fill='both', expand=True)

        center_column = tk.Frame(main_container, bg=self.COLORS['bg_primary'])
        center_column.pack(side='left', fill='both', expand=True, padx=20)

        right_column = tk.Frame(main_container, bg=self.COLORS['bg_primary'])
        right_column.pack(side='right', fill='both', expand=True)

        self.setup_left_column(left_column)
        self.setup_center_column(center_column)
        self.setup_right_column(right_column)

    # ─────────────────────────────────────────────────────────────────────────
    def setup_top_indicators(self):
        top_frame = tk.Frame(self.root, bg=self.COLORS['bg_card'], height=100)
        top_frame.pack(fill='x', padx=20, pady=(0, 10))
        top_frame.pack_propagate(False)

        for label_text, value_text, unit_text, color, attr in [
            ("📅 ДЕНЬ ЭКСПЕРИМЕНТА", "0", f"из {self.max_days} дней",
             self.COLORS['accent_green'], 'day_label'),
            ("🏆 НАУЧНЫЕ ОЧКИ", "0", "накоплено",
             self.COLORS['accent_orange'], 'score_label'),
            ("🔬 ОТКРЫТИЯ", "0", "сделано",
             self.COLORS['accent_blue'], 'discovery_count_label'),
            ("👨‍🚀 ЭКИПАЖ", str(self.crew_members), "человек",
             self.COLORS['success'], None),
        ]:
            card = tk.Frame(top_frame, bg=self.COLORS['bg_secondary'])
            card.pack(side='left', fill='both', expand=True, padx=5, pady=10)
            tk.Label(card, text=label_text, font=('SegoeUI', 9, 'bold'),
                     fg=self.COLORS['text_secondary'],
                     bg=self.COLORS['bg_secondary']).pack(pady=(10, 0))
            lbl = tk.Label(card, text=value_text, font=('SegoeUI', 24, 'bold'),
                           fg=color, bg=self.COLORS['bg_secondary'])
            lbl.pack()
            tk.Label(card, text=unit_text, font=('SegoeUI', 9),
                     fg=self.COLORS['text_secondary'],
                     bg=self.COLORS['bg_secondary']).pack()
            if attr:
                setattr(self, attr, lbl)

        # ── ИСПРАВЛЕНИЕ 3: метка деградации ────────────────────────────────
        self.degradation_label = tk.Label(top_frame,
            text="⚙️ Системы: НОРМА",
            font=('SegoeUI', 10, 'bold'),
            fg=self.COLORS['success'],
            bg=self.COLORS['bg_secondary'])
        degrad_card = tk.Frame(top_frame, bg=self.COLORS['bg_secondary'])
        degrad_card.pack(side='left', fill='both', expand=True, padx=5, pady=10)
        tk.Label(degrad_card, text="⚙️ СОСТОЯНИЕ СИСТЕМ",
                 font=('SegoeUI', 9, 'bold'),
                 fg=self.COLORS['text_secondary'],
                 bg=self.COLORS['bg_secondary']).pack(pady=(10, 0))
        self.degradation_label = tk.Label(degrad_card,
            text="НОРМА", font=('SegoeUI', 14, 'bold'),
            fg=self.COLORS['success'], bg=self.COLORS['bg_secondary'])
        self.degradation_label.pack()
        tk.Label(degrad_card, text="тех. состояние",
                 font=('SegoeUI', 9), fg=self.COLORS['text_secondary'],
                 bg=self.COLORS['bg_secondary']).pack()

    # ─────────────────────────────────────────────────────────────────────────
    def setup_left_column(self, parent):
        resources_frame = tk.Frame(parent, bg=self.COLORS['bg_card'])
        resources_frame.pack(fill='both', expand=True)
        tk.Label(resources_frame, text="📊 РЕСУРСЫ СИСТЕМЫ",
                 font=('SegoeUI', 12, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_card']).pack(pady=(15, 10))

        # (name, attr, unit, color_ok, max_val, critical_low, critical_high)
        resources = [
            ("🌿 Биомасса",   "plant_biomass_kg", "кг", self.COLORS['success'],  300, 10,   None),
            ("💨 Кислород",    "oxygen_kg",        "кг", self.COLORS['accent_blue'], 300, 30, None),
            ("🌫️ CO₂",        "co2_kg",           "кг", self.COLORS['warning'],  200, None, 120),
            ("💧 Вода",        "water_liters",     "л",  '#3498db',               500, 40,   None),
            ("🍎 Пища",        "food_kg",          "кг", self.COLORS['accent_orange'], 100, 8, None),
            ("⚡ Энергия",     "energy_kwh",       "кВт·ч", '#f1c40f',           300, 15,   None),
            ("♻️ Отходы",      "waste_kg",         "кг", self.COLORS['accent_purple'], 100, None, 80),
            ("😊 Экипаж",      "crew_happiness",   "%",  self.COLORS['danger'],   100, 25,   None),
        ]
        self.resource_indicators = {}

        for i in range(0, len(resources), 2):
            row_frame = tk.Frame(resources_frame, bg=self.COLORS['bg_card'])
            row_frame.pack(fill='x', padx=15, pady=5)
            for j in range(2):
                if i + j < len(resources):
                    name, key, unit, color, max_val, crit_low, crit_high = resources[i + j]
                    card = tk.Frame(row_frame, bg=self.COLORS['bg_secondary'])
                    card.pack(side='left', fill='both', expand=True, padx=5)
                    tk.Label(card, text=name, font=('SegoeUI', 9, 'bold'),
                             fg=color, bg=self.COLORS['bg_secondary']).pack(anchor='w', padx=10, pady=(10, 5))
                    value = getattr(self, key)
                    value_label = tk.Label(card, text=f"{value:.1f} {unit}",
                                           font=('SegoeUI', 18, 'bold'),
                                           fg='white', bg=self.COLORS['bg_secondary'])
                    value_label.pack(pady=(0, 5))
                    progress_frame = tk.Frame(card, bg='#34495e', height=8, width=150)
                    progress_frame.pack(pady=(0, 10))
                    progress_frame.pack_propagate(False)
                    pw = max(2, min(150, int((value / max_val) * 150)))
                    progress = tk.Frame(progress_frame, bg=color, height=8, width=pw)
                    progress.pack(side='left')
                    self.resource_indicators[key] = {
                        'value': value_label, 'progress': progress,
                        'color': color, 'max': max_val,
                        'crit_low': crit_low, 'crit_high': crit_high,
                        'unit': unit
                    }

        self.analyze_btn = tk.Button(resources_frame,
                                     text="📈 ПРОВЕСТИ НАУЧНЫЙ АНАЛИЗ",
                                     font=('SegoeUI', 11, 'bold'),
                                     bg=self.COLORS['accent_blue'],
                                     fg='white', relief='flat',
                                     command=self.scientific_analysis, height=2)
        self.analyze_btn.pack(fill='x', padx=20, pady=20)

    # ─────────────────────────────────────────────────────────────────────────
    def setup_center_column(self, parent):
        chart_frame = tk.Frame(parent, bg=self.COLORS['bg_card'])
        chart_frame.pack(fill='both', expand=True)
        tk.Label(chart_frame, text="📈 ДИНАМИКА ЭКОСИСТЕМЫ",
                 font=('SegoeUI', 12, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_card']).pack(pady=(15, 10))

        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor=self.COLORS['bg_card'])
        plt.style.use('dark_background')
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=10)

        self.next_day_btn = tk.Button(chart_frame,
                                      text="➡️ СЛЕДУЮЩИЙ ДЕНЬ ЭКСПЕРИМЕНТА",
                                      font=('SegoeUI', 12, 'bold'),
                                      bg=self.COLORS['accent_purple'],
                                      fg='white', relief='flat',
                                      command=self.next_day, height=2)
        self.next_day_btn.pack(fill='x', padx=20, pady=(10, 15))

    # ─────────────────────────────────────────────────────────────────────────
    def setup_right_column(self, parent):
        experiments_frame = tk.Frame(parent, bg=self.COLORS['bg_card'])
        experiments_frame.pack(fill='both', expand=True, pady=(0, 10))
        tk.Label(experiments_frame, text="🔬 НАУЧНЫЕ ЭКСПЕРИМЕНТЫ",
                 font=('SegoeUI', 12, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_card']).pack(pady=(15, 10))

        # ── ИСПРАВЛЕНИЕ 4: добавлены «Обслуживание систем» и «Добавить энергию» ─
        experiments = [
            ("🌱 Посадить хлореллу",    self.plant_chlorella,     self.COLORS['success']),
            ("💡 Усилить фотосинтез",   self.boost_photosynthesis, self.COLORS['accent_green']),
            ("🔄 Запустить рециклинг",  self.start_recycling,      self.COLORS['accent_blue']),
            ("🧪 Анализ проб",          self.analyze_samples,      self.COLORS['accent_purple']),
            ("🔬 Улучшить фильтры",     self.upgrade_filters,      self.COLORS['warning']),
            ("🌾 Собрать урожай",       self.harvest_crops,        self.COLORS['accent_orange']),
            ("🛠️ Обслуживание систем",  self.maintain_systems,     '#e74c3c'),
            ("☀️ Солнечные панели",     self.boost_energy,         '#f39c12'),
        ]
        self.experiment_buttons = []

        for i in range(0, len(experiments), 2):
            row_frame = tk.Frame(experiments_frame, bg=self.COLORS['bg_card'])
            row_frame.pack(fill='x', padx=15, pady=5)
            for j in range(2):
                if i + j < len(experiments):
                    text, command, color = experiments[i + j]
                    btn = tk.Button(row_frame, text=text,
                                    font=('SegoeUI', 10, 'bold'),
                                    bg=color, fg='white', relief='flat',
                                    command=command, height=2, width=20)
                    btn.pack(side='left', fill='both', expand=True, padx=5)
                    self.experiment_buttons.append(btn)

        # Лог событий
        log_frame = tk.Frame(parent, bg=self.COLORS['bg_card'])
        log_frame.pack(fill='both', expand=True)
        tk.Label(log_frame, text="📝 НАУЧНЫЙ ЖУРНАЛ",
                 font=('SegoeUI', 12, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_card']).pack(pady=(15, 10))

        self.log_text = tk.Text(log_frame, height=8,
                                bg=self.COLORS['bg_secondary'], fg='white',
                                font=('Consolas', 9), wrap='word',
                                relief='flat', borderwidth=0)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=(0, 15))
        scrollbar.pack(side='right', fill='y', pady=(0, 15))
        self.log_text.config(state='disabled')

        # Факты
        facts_frame = tk.Frame(parent, bg=self.COLORS['bg_card'])
        facts_frame.pack(fill='both', expand=True, pady=(10, 0))
        tk.Label(facts_frame, text="🔍 ФАКТЫ О БИОС-3",
                 font=('SegoeUI', 12, 'bold'),
                 fg=self.COLORS['text_primary'],
                 bg=self.COLORS['bg_card']).pack(pady=(15, 10))
        self.fact_label = tk.Label(facts_frame, text="",
                                   font=('SegoeUI', 10),
                                   fg=self.COLORS['text_secondary'],
                                   bg=self.COLORS['bg_secondary'],
                                   wraplength=350, justify='left',
                                   height=4, padx=15, pady=15)
        self.fact_label.pack(fill='x', padx=15, pady=(0, 10))
        nav_frame = tk.Frame(facts_frame, bg=self.COLORS['bg_card'])
        nav_frame.pack(pady=(0, 15))
        tk.Button(nav_frame, text="← Предыдущий", font=('SegoeUI', 9),
                  bg=self.COLORS['bg_secondary'], fg=self.COLORS['text_secondary'],
                  relief='flat', command=self.prev_fact).pack(side='left', padx=5)
        tk.Button(nav_frame, text="Следующий →", font=('SegoeUI', 9),
                  bg=self.COLORS['bg_secondary'], fg=self.COLORS['text_secondary'],
                  relief='flat', command=self.next_fact).pack(side='left', padx=5)

    # ─────────────────────────────────────────────────────────────────────────
    def update_display(self):
        if self.game_over:
            return

        for key, ind in self.resource_indicators.items():
            value = getattr(self, key)

            # ── ИСПРАВЛЕНИЕ 3: цвет меняется при критических значениях ─────
            text_color = 'white'
            crit_low = ind.get('crit_low')
            crit_high = ind.get('crit_high')
            if crit_low is not None and value <= crit_low * 1.5:
                text_color = self.COLORS['danger']   # красный — опасно мало
            elif crit_high is not None and value >= crit_high * 0.85:
                text_color = self.COLORS['warning']  # оранжевый — почти предел
            if crit_low is not None and value <= crit_low:
                text_color = '#ff0000'  # ярко-красный — критично

            unit = ind.get('unit', '')
            if key == 'crew_happiness':
                ind['value'].config(text=f"{value:.0f} {unit}", fg=text_color)
            else:
                ind['value'].config(text=f"{value:.1f} {unit}", fg=text_color)

            pw = max(2, min(150, int((value / ind['max']) * 150)))
            bar_color = ind['color']
            if text_color in (self.COLORS['danger'], '#ff0000'):
                bar_color = self.COLORS['danger']
            ind['progress'].config(width=pw, bg=bar_color)

        self.day_label.config(text=str(self.day))
        self.score_label.config(text=str(self.research_points))
        self.discovery_count_label.config(text=str(len(self.discoveries)))

        # Состояние деградации
        avg_eff = (self.photosynthesis_modifier + self.filter_modifier) / 2
        if avg_eff >= 0.85:
            deg_text, deg_color = "НОРМА", self.COLORS['success']
        elif avg_eff >= 0.65:
            deg_text, deg_color = "ВНИМАНИЕ", self.COLORS['warning']
        elif avg_eff >= 0.45:
            deg_text, deg_color = "ДЕГРАДАЦИЯ", self.COLORS['accent_red']
        else:
            deg_text, deg_color = "АВАРИЯ!", '#ff0000'
        self.degradation_label.config(text=deg_text, fg=deg_color)

        self.update_chart()

    # ─────────────────────────────────────────────────────────────────────────
    def update_chart(self):
        self.ax.clear()
        colors = ['#00d2b8','#00a8ff','#ff9f43','#3498db','#ff6b6b','#f1c40f','#9c88ff','#e74c3c']
        metrics = ['plant_biomass','oxygen','co2','water','food','energy','waste','happiness']
        labels  = ['Биомасса','O₂','CO₂','Вода','Еда','Энергия','Отходы','Экипаж']
        for i, metric in enumerate(metrics):
            if metric in self.history:
                self.ax.plot(self.history['days'], self.history[metric],
                             color=colors[i], label=labels[i],
                             linewidth=3, marker='o', markersize=4,
                             markeredgecolor='white', markeredgewidth=1)
        self.ax.set_facecolor(self.COLORS['bg_secondary'])
        self.fig.patch.set_facecolor(self.COLORS['bg_card'])
        self.ax.tick_params(colors='white', labelsize=10)
        self.ax.set_xlabel('Дни', color='white', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Показатели', color='white', fontsize=12, fontweight='bold')
        self.ax.set_title('Динамика экосистемы БИОС-3',
                          color='white', fontsize=14, fontweight='bold', pad=20)
        self.ax.legend(facecolor=self.COLORS['bg_secondary'], edgecolor='none',
                       labelcolor='white', fontsize=9, loc='upper left',
                       bbox_to_anchor=(0.02, 0.98))
        self.ax.grid(True, alpha=0.2, linestyle='--')
        self.ax.autoscale_view()
        self.fig.tight_layout()
        self.canvas.draw()

    # ─────────────────────────────────────────────────────────────────────────
    def log_event(self, event, scientific=False):
        if self.game_over:
            return
        self.log_text.config(state='normal')
        prefix = "🔬 " if scientific else "📅 "
        self.log_text.insert('end', f"{prefix}День {self.day}: {event}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def show_science_tip(self):
        self.fact_label.config(text=self.science_facts[self.current_fact])

    def next_fact(self):
        self.current_fact = (self.current_fact + 1) % len(self.science_facts)
        self.show_science_tip()

    def prev_fact(self):
        self.current_fact = (self.current_fact - 1) % len(self.science_facts)
        self.show_science_tip()

    # ─────────────────────────────────────────────────────────────────────────
    def _record_action(self):
        """Вызывается каждым экспериментом — сбрасывает деградацию."""
        self.actions_taken_today += 1

    def _can_act(self):
        """FIX-6: Проверяет, не исчерпан ли лимит действий в день."""
        if self.actions_taken_today >= self.max_actions_per_day:
            messagebox.showinfo("Лимит действий",
                f"Экипаж может выполнить не более {self.max_actions_per_day} экспериментов в день.\n"
                "Переходите к следующему дню!")
            return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # ЭКСПЕРИМЕНТЫ
    # ─────────────────────────────────────────────────────────────────────────
    def plant_chlorella(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.water_liters >= 20 and self.energy_kwh >= 10:
            self.plant_biomass_kg += 20
            self.water_liters -= 20
            self.energy_kwh -= 10
            self._record_action()
            self.log_event("Посажена хлорелла — биомасса +20 кг", scientific=True)
            self.research_points += 2
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно ресурсов!", "Нужно 20 л воды и 10 кВт·ч")

    def boost_photosynthesis(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.energy_kwh >= 20 and self.co2_kg >= 10:
            self.oxygen_kg += 15
            self.co2_kg -= 10
            self.energy_kwh -= 20
            # Частичное восстановление фотосинтеза
            self.photosynthesis_modifier = min(1.0, self.photosynthesis_modifier + 0.1)
            self._record_action()
            self.log_event("Усилен фотосинтез — O₂ +15 кг, фотосинтез +10%", scientific=True)
            if random.random() > 0.7 and "Оптимальный режим фотосинтеза" not in self.discoveries:
                self.discoveries.append("Оптимальный режим фотосинтеза")
                self.research_points += 10
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно ресурсов!", "Нужно 20 кВт·ч и 10 кг CO₂")

    def start_recycling(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        # ── ИСПРАВЛЕНИЕ 5: снижен порог — теперь 10 кг отходов (было 20) ──
        if self.energy_kwh >= 25 and self.waste_kg >= 10:
            recycled = min(120, self.waste_kg * 0.8 * self.water_recycler_efficiency)
            self.water_liters += recycled
            self.waste_kg = max(0, self.waste_kg - min(self.waste_kg, recycled * 0.6))
            self.energy_kwh -= 25
            self._record_action()
            self.log_event(f"Рециркуляция — вода +{recycled:.1f} л", scientific=True)
            if random.random() > 0.8:
                self.water_recycler_efficiency = min(0.95, self.water_recycler_efficiency + 0.05)
                self.log_event("Эффективность рециркуляции улучшена!", scientific=True)
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно ресурсов!", "Нужно 25 кВт·ч и 10 кг отходов")

    def analyze_samples(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.energy_kwh >= 10:
            pts = random.randint(3, 8)
            self.research_points += pts
            self.energy_kwh -= 10
            self._record_action()
            discoveries = [
                "Обнаружены новые штаммы микроорганизмов",
                "Определена оптимальная концентрация CO₂",
                "Измерена эффективность фотосинтеза",
                "Проанализирован состав биомассы"
            ]
            d = random.choice(discoveries)
            if d not in self.discoveries:
                self.discoveries.append(d)
                self.research_points += 5
            self.log_event(f"Анализ проб: +{pts} очков", scientific=True)
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно энергии!", "Нужно 10 кВт·ч")

    def upgrade_filters(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.energy_kwh >= 20:
            self.air_filter_efficiency = min(0.95, self.air_filter_efficiency + 0.08)
            self.filter_modifier = min(1.0, self.filter_modifier + 0.15)
            self.energy_kwh -= 20
            self._record_action()
            self.log_event(f"Фильтры улучшены до {self.air_filter_efficiency*100:.0f}%",
                           scientific=True)
            self.research_points += 3
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно энергии!", "Нужно 20 кВт·ч")

    def harvest_crops(self):
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.plant_biomass_kg >= 20:
            food_yield = 12 * (self.crew_happiness / 100)
            self.food_kg += food_yield
            self.plant_biomass_kg -= 20
            self._record_action()
            self.log_event(f"Урожай собран: +{food_yield:.1f} кг пищи", scientific=True)
            self.research_points += 2
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно биомассы!", "Нужно 20 кг биомассы")

    def maintain_systems(self):
        """НОВЫЙ эксперимент: обслуживание систем — восстанавливает модификаторы."""
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.energy_kwh >= 15:
            old_p = self.photosynthesis_modifier
            old_f = self.filter_modifier
            self.photosynthesis_modifier = min(1.0, self.photosynthesis_modifier + 0.18)
            self.filter_modifier = min(1.0, self.filter_modifier + 0.18)
            self.energy_kwh -= 15
            self._record_action()
            dp = (self.photosynthesis_modifier - old_p) * 100
            df = (self.filter_modifier - old_f) * 100
            self.log_event(f"Обслуживание: фотосинтез +{dp:.0f}%, фильтр +{df:.0f}%",
                           scientific=True)
            self.research_points += 2
            self.update_display()
        else:
            messagebox.showwarning("Недостаточно энергии!", "Нужно 15 кВт·ч")

    def boost_energy(self):
        """Настройка солнечных панелей — с кулдауном (FIX-5)."""
        if self.game_over:
            return
        if not self._can_act():
            return
        if self.solar_cooldown > 0:
            messagebox.showinfo("Кулдаун",
                f"Панели недавно настраивались.\nДоступно через {self.solar_cooldown} дн.")
            return
        if self.energy_kwh < 5:
            messagebox.showwarning("Недостаточно энергии!", "Нужно 5 кВт·ч на настройку")
            return
        self.energy_kwh -= 5  # затраты на настройку
        bonus = random.randint(25, 50)
        self.energy_kwh = min(300, self.energy_kwh + bonus)
        self.solar_cooldown = 2  # доступно снова через 2 дня
        self._record_action()
        self.log_event(f"Солнечные панели настроены: +{bonus} кВт·ч (след. настройка через 2 дня)", scientific=True)
        self.research_points += 2
        self.update_display()

    # ─────────────────────────────────────────────────────────────────────────
    def scientific_analysis(self):
        if self.game_over:
            return
        # Анализ использует те же формулы, что и next_day
        o2_prod = (self.plant_biomass_kg * self.SCIENTIFIC_CONSTANTS['photosynthesis_rate']
                   * 0.1 * self.photosynthesis_modifier)
        plant_resp = self.plant_biomass_kg * 0.02
        crew_resp  = self.crew_members * 1.0
        o2_cons = plant_resp + crew_resp
        o2_bal  = o2_prod - o2_cons

        co2_from_resp = (plant_resp * self.SCIENTIFIC_CONSTANTS['co2_respiration_ratio']
                         + crew_resp)
        co2_consumed_photo = o2_prod * self.SCIENTIFIC_CONSTANTS['co2_assimilation']
        co2_bal = co2_from_resp - co2_consumed_photo

        # FIX-1: водный баланс с транспирацией от биомассы
        plant_transp = self.plant_biomass_kg * self.SCIENTIFIC_CONSTANTS['plant_transpiration_rate']
        water_cons = (self.crew_members * self.SCIENTIFIC_CONSTANTS['human_water_consumption']
                      + plant_transp)
        water_rec  = self.waste_kg * 0.12 * self.water_recycler_efficiency
        energy_need = self.grow_area * self.SCIENTIFIC_CONSTANTS['energy_per_sqm'] + self.crew_members * 2
        days_energy = self.energy_kwh / energy_need if energy_need > 0 else 0

        lines = [
            f"{'✅' if o2_bal > 0 else '⚠️'} Баланс O₂: {o2_bal:+.2f} кг/день",
            f"🌫️ Баланс CO₂: {co2_bal:+.2f} кг/день",
            f"💧 Водный баланс: {water_rec - water_cons:.2f} л/день",
            f"  ├ расход экипажа: {self.crew_members * 2.5:.1f} л, транспирация: {plant_transp:.1f} л",
            f"⚡ Энергии хватит на: {days_energy:.1f} дней",
            f"📉 КПД фотосинтеза: {self.photosynthesis_modifier*100:.0f}%",
            f"📉 КПД фильтров: {self.filter_modifier * self.air_filter_efficiency * 100:.0f}%",
            f"🔄 Действий сегодня: {self.actions_taken_today}/{self.max_actions_per_day}",
        ]
        recs = []
        if o2_bal < 0:
            recs.append("• Посадите хлореллу или усильте фотосинтез")
        if self.co2_kg > 100:
            recs.append("• Улучшите фильтры или нарастите биомассу")
        if self.water_liters < 100:
            recs.append("• Срочно запустите рециркуляцию воды!")
        if self.food_kg < 15:
            recs.append("• Пора собирать урожай!")
        if self.photosynthesis_modifier < 0.7:
            recs.append("• Выполните обслуживание систем — КПД упал!")

        msg = "🔬 НАУЧНЫЙ АНАЛИЗ СИСТЕМЫ:\n\n" + "\n".join(lines)
        if recs:
            msg += "\n\n📋 РЕКОМЕНДАЦИИ:\n" + "\n".join(recs)
        self._create_analysis_window(msg)
        self.log_event("Научный анализ выполнен", scientific=True)
        self.research_points += 3
        self._record_action()
        self.update_display()

    def _create_analysis_window(self, message):
        w = tk.Toplevel(self.root)
        w.title("Научный анализ системы")
        w.geometry("500x430")
        w.configure(bg=self.COLORS['bg_primary'])
        w.resizable(False, False)
        tk.Label(w, text="🔬 АНАЛИЗ СИСТЕМЫ",
                 font=('SegoeUI', 16, 'bold'),
                 fg=self.COLORS['accent_green'],
                 bg=self.COLORS['bg_primary']).pack(pady=20)
        tf = tk.Frame(w, bg=self.COLORS['bg_card'])
        tf.pack(fill='both', expand=True, padx=20, pady=10)
        txt = tk.Text(tf, wrap='word', font=('SegoeUI', 10),
                      bg=self.COLORS['bg_card'], fg='white', relief='flat')
        sb = tk.Scrollbar(tf, command=txt.yview)
        txt.config(yscrollcommand=sb.set)
        txt.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        sb.pack(side='right', fill='y', pady=10)
        txt.insert('1.0', message)
        txt.config(state='disabled')
        tk.Button(w, text="ЗАКРЫТЬ", font=('SegoeUI', 11, 'bold'),
                  bg=self.COLORS['accent_blue'], fg='white', relief='flat',
                  command=w.destroy).pack(pady=15)

    # ─────────────────────────────────────────────────────────────────────────
    def next_day(self):
        """Основная игровая логика — один ход."""
        if self.game_over:
            return
        if self.day >= self.max_days:
            return

        self.day += 1

        # ── FIX-5: обновление кулдауна солнечных панелей ──────────────────
        if self.solar_cooldown > 0:
            self.solar_cooldown -= 1

        # ── Деградация при бездействии ─────────────────────────────────────
        if self.actions_taken_today == 0:
            self.photosynthesis_modifier = max(0.3, self.photosynthesis_modifier - 0.07)
            self.filter_modifier         = max(0.3, self.filter_modifier         - 0.05)
            self.log_event("⚠️ Системы не обслуживались — КПД снизился!", scientific=False)
        else:
            self.photosynthesis_modifier = max(0.3, self.photosynthesis_modifier - 0.01)
            self.filter_modifier         = max(0.3, self.filter_modifier         - 0.01)

        self.actions_taken_today = 0  # сброс для следующего дня

        # ── FIX-2: ФОТОСИНТЕЗ (увеличен k_ph до 0.045) ───────────────────
        o2_produced  = (self.plant_biomass_kg
                        * self.SCIENTIFIC_CONSTANTS['photosynthesis_rate']
                        * 0.1
                        * self.photosynthesis_modifier)
        co2_consumed = o2_produced * self.SCIENTIFIC_CONSTANTS['co2_assimilation']
        self.oxygen_kg += o2_produced
        self.co2_kg    -= min(co2_consumed, self.co2_kg * 0.8)

        # ── FIX-4: ДЫХАНИЕ (стехиометрия CO₂ для растений) ────────────────
        plant_resp = self.plant_biomass_kg * 0.02
        crew_resp  = self.crew_members * 1.0
        self.oxygen_kg -= (plant_resp + crew_resp)
        # CO₂ от дыхания: растения выделяют CO₂ с коэффициентом 44/32 = 1.375
        self.co2_kg    += (plant_resp * self.SCIENTIFIC_CONSTANTS['co2_respiration_ratio']
                           + crew_resp)

        # ── FIX-1: ПОТРЕБЛЕНИЕ ВОДЫ (транспирация зависит от биомассы) ─────
        plant_transpiration = (self.plant_biomass_kg
                               * self.SCIENTIFIC_CONSTANTS['plant_transpiration_rate'])
        self.water_liters -= (self.crew_members * self.SCIENTIFIC_CONSTANTS['human_water_consumption']
                              + plant_transpiration)
        self.food_kg      -= self.crew_members * self.SCIENTIFIC_CONSTANTS['human_food_consumption']
        self.energy_kwh   -= self.crew_members * 1.5

        # ── FIX-8: АВТОМАТИЧЕСКАЯ СОЛНЕЧНАЯ ГЕНЕРАЦИЯ ──────────────────────
        # БИОС-3 получал электроэнергию от внешнего источника непрерывно.
        # Базовая мощность солнечных панелей: +12 кВт·ч/сут (без действий игрока).
        self.energy_kwh = min(300, self.energy_kwh + 12)

        # ── FIX-3: РОСТ РАСТЕНИЙ (зависит от CO₂, а НЕ от O₂) ────────────
        if self.water_liters > 0 and self.co2_kg > 0:
            growth = (self.plant_biomass_kg
                      * self.SCIENTIFIC_CONSTANTS['plant_growth_rate']
                      * max(0, self.water_liters) / 300
                      * max(0, self.co2_kg) / 100       # FIX-3: CO₂ вместо O₂
                      * self.photosynthesis_modifier)
            self.plant_biomass_kg += growth

        # ── ОТХОДЫ ────────────────────────────────────────────────────────
        self.waste_kg += self.crew_members * 0.5 + self.plant_biomass_kg * 0.01

        # ── FIX-7: АВТОМАТИЧЕСКАЯ РЕЦИРКУЛЯЦИЯ (выровнена с HTML-версией) ─
        if self.energy_kwh > 20 and self.waste_kg > 5:
            recycled = self.waste_kg * 0.12 * self.water_recycler_efficiency
            self.water_liters += recycled
            self.waste_kg     *= 0.92
            self.energy_kwh   -= 3

        # ── ФИЛЬТРАЦИЯ ВОЗДУХА (с учётом деградации) ──────────────────────
        if self.energy_kwh > 10:
            filtered = min(3.5, self.co2_kg * 0.07 * self.air_filter_efficiency * self.filter_modifier)
            self.co2_kg     -= filtered
            self.energy_kwh -= 2

        # ── СЧАСТЬЕ ЭКИПАЖА ───────────────────────────────────────────────
        dhappy = 0
        if self.oxygen_kg > 150 and self.co2_kg < 80:
            dhappy += random.randint(1, 2)
        if self.food_kg > 15:
            dhappy += random.randint(0, 1)
        if self.oxygen_kg < 50:
            dhappy -= random.randint(3, 5)
        if self.co2_kg > 100:
            dhappy -= random.randint(2, 4)
        if self.food_kg < 10:
            dhappy -= random.randint(2, 4)
        if self.photosynthesis_modifier < 0.5:
            dhappy -= random.randint(1, 3)  # экипаж видит деградацию
        self.crew_happiness = max(0, min(100, self.crew_happiness + dhappy))

        # ── СЛУЧАЙНЫЕ СОБЫТИЯ ─────────────────────────────────────────────
        if random.random() < 0.25:
            self.random_event()

        # ── ОГРАНИЧЕНИЯ ───────────────────────────────────────────────────
        self.oxygen_kg        = max(0, self.oxygen_kg)
        self.water_liters     = max(0, self.water_liters)
        self.food_kg          = max(0, self.food_kg)
        self.plant_biomass_kg = max(0, min(300, self.plant_biomass_kg))
        self.co2_kg           = max(0, min(200, self.co2_kg))
        self.energy_kwh       = max(0, min(300, self.energy_kwh))
        self.waste_kg         = max(0, min(100, self.waste_kg))

        # Запись истории
        for key in ['plant_biomass','oxygen','co2','water','food','energy','waste','happiness']:
            attrs = {'plant_biomass': 'plant_biomass_kg', 'oxygen': 'oxygen_kg',
                     'co2': 'co2_kg', 'water': 'water_liters', 'food': 'food_kg',
                     'energy': 'energy_kwh', 'waste': 'waste_kg', 'happiness': 'crew_happiness'}
            self.history[key].append(getattr(self, attrs[key]))
        self.history['days'].append(self.day)

        if self.day % 3 == 0:
            self.log_event("Автомониторинг завершён", scientific=True)

        self.update_display()

        # ── Проверка завершения ──────────────────────────────────────────
        # Если дошли до дня 14 — ПОБЕДА (даже при низких ресурсах: экипаж дожил!)
        if self.day >= self.max_days:
            self.game_over = True
            self.disable_game_buttons()
            score = self._compute_score()
            self.show_result_window(is_victory=True, score=score)
            return

        issues = self.check_game_over()
        if issues:
            self.game_over = True
            self.disable_game_buttons()
            self.show_result_window(is_victory=False, issues=issues)

    # ─────────────────────────────────────────────────────────────────────────
    def random_event(self):
        events = [
            ("Солнечная вспышка! +20 кВт·ч",               "energy",  20),
            ("Обнаружен лёд: +40 л воды",                   "water",   40),
            ("Открытие экипажа!",                            "research",12),
            ("Поломка рециркуляции (−0.1 КПД)",              "recycler",-0.1),
            ("Вспышка роста водорослей: +20 кг биомассы",    "plant",   20),
            ("Микроутечка кислорода: −20 кг",                "oxygen", -20),
            ("Экипаж воодушевлён: +10% морального духа",     "happy",   10),
            ("Пылевая буря: −15 кВт·ч",                      "energy", -15),
            ("Конденсация: +25 л воды",                      "water",   25),
        ]
        event, res, chg = random.choice(events)
        if   res == "energy":   self.energy_kwh          = max(0, min(300, self.energy_kwh + chg))
        elif res == "water":    self.water_liters         = max(0, self.water_liters + chg)
        elif res == "research": self.research_points     += chg
        elif res == "recycler": self.water_recycler_efficiency = max(0.3, self.water_recycler_efficiency + chg)
        elif res == "plant":    self.plant_biomass_kg     = max(0, self.plant_biomass_kg + chg)
        elif res == "oxygen":   self.oxygen_kg            = max(0, self.oxygen_kg + chg)
        elif res == "happy":    self.crew_happiness       = max(0, min(100, self.crew_happiness + chg))
        self.log_event(f"📢 {event}")

    # ─────────────────────────────────────────────────────────────────────────
    def check_game_over(self):
        issues = []
        if self.oxygen_kg    <= 10:  issues.append("Критически мало кислорода (<10 кг)")
        if self.water_liters <= 20:  issues.append("Критически мало воды (<20 л)")
        if self.food_kg      <=  5:  issues.append("Критически мало пищи (<5 кг)")
        if self.energy_kwh   <= 10:  issues.append("Критически мало энергии (<10 кВт·ч)")
        if self.co2_kg       >= 150: issues.append("Критически высокий CO₂ (>150 кг)")
        if self.crew_happiness<= 20: issues.append("Критически низкий моральный дух экипажа")
        return issues if issues else False

    # ─────────────────────────────────────────────────────────────────────────
    def _compute_score(self):
        s  = min(100, self.oxygen_kg    / 200 * 100) * 0.25
        s += max(0, 100 - self.co2_kg  / 200 * 100) * 0.15
        s += min(100, self.water_liters / 3)          * 0.10
        s += min(100, self.food_kg * 2)               * 0.10
        s += min(100, self.energy_kwh / 2)            * 0.10
        s += self.crew_happiness                       * 0.10
        s += min(100, self.plant_biomass_kg)           * 0.05
        s += min(50,  self.research_points * 0.5)
        return min(100, s)

    # ─────────────────────────────────────────────────────────────────────────
    def disable_game_buttons(self):
        """Блокирует ВСЕ кнопки после завершения игры."""
        # ── ИСПРАВЛЕНИЕ 6: расширена блокировка ─────────────────────────────
        for btn in ([self.next_day_btn, self.analyze_btn] + self.experiment_buttons):
            if btn is not None:
                try:
                    btn.config(state='disabled', bg='#555566')
                except tk.TclError:
                    pass

    # ─────────────────────────────────────────────────────────────────────────
    def show_result_window(self, is_victory, issues=None, score=0):
        result_window = tk.Toplevel(self.root)
        result_window.title("Результат эксперимента")
        result_window.geometry("520x420")
        result_window.resizable(False, False)

        bg = '#00d2b8' if is_victory else '#c0392b'
        result_window.configure(bg=bg)

        if is_victory:
            title = "🏆 ПОБЕДА!"
            msg   = (f"Эксперимент успешно завершён!\n\n"
                     f"Вы создали стабильную замкнутую экосистему.\n\n"
                     f"Научный рейтинг: {score:.1f}%\n\n"
                     f"Миссия выполнена! Экипаж возвращается на Землю героями.")
        else:
            title = "💀 МИССИЯ ПРОВАЛЕНА"
            msg   = "Критические проблемы:\n\n" + "\n".join(f"• {i}" for i in issues)
            msg  += "\n\nЭкосистема не может поддерживать жизнь.\nМиссия прервана."

        tk.Label(result_window, text=title,
                 font=('SegoeUI', 24, 'bold'), fg='white', bg=bg).pack(pady=30)
        tk.Label(result_window, text=msg,
                 font=('SegoeUI', 11), fg='white', bg=bg,
                 wraplength=460, justify='left').pack(pady=10, padx=20)
        tk.Button(result_window, text="ЗАКРЫТЬ ИГРУ",
                  font=('SegoeUI', 12, 'bold'),
                  bg='white', fg=bg, relief='flat',
                  command=lambda: [result_window.destroy(), self.root.destroy()]).pack(pady=30)

        result_window.transient(self.root)
        result_window.grab_set()
        result_window.focus_set()
        result_window.update_idletasks()
        w, h = result_window.winfo_width(), result_window.winfo_height()
        x = result_window.winfo_screenwidth()  // 2 - w // 2
        y = result_window.winfo_screenheight() // 2 - h // 2
        result_window.geometry(f'{w}x{h}+{x}+{y}')


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceEcosystemGame(root)
    root.mainloop()