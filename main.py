import cv2
import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

# Try importing MediaPipe safely
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    HAS_MEDIAPIPE = True
except Exception as e:
    print(f"[MediaPipe Warning]: {e}")
    HAS_MEDIAPIPE = False

# Native Mobile TTS via Plyer
try:
    from plyer import tts
except ImportError:
    tts = None

# Set Neon-Dark Background Theme
Window.clearcolor = (0.05, 0.07, 0.1, 1)


# ==========================================
# 1. LIVE CAMERA & MEDIAPIPE CORE WIDGET
# ==========================================
class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start_camera(self):
        # Sa Android APK, 0 ang karaniwang rear camera; fallback sa 1 kung kailangan
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(1)
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # 30 FPS

    def stop_camera(self):
        if self.capture:
            Clock.unschedule(self.update)
            self.capture.release()
            self.capture = None

    def update(self, dt):
        if not self.capture or not self.capture.isOpened():
            return

        ret, frame = self.capture.read()
        if not ret or frame is None:
            return

        # Horizontal flip para sa selfie/mirror view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe Landmark Detection
        if HAS_MEDIAPIPE:
            try:
                results = hands_detector.process(rgb_frame)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_draw.draw_landmarks(
                            rgb_frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )
            except Exception as err:
                print(f"[Landmark Error]: {err}")

        # Convert Frame -> Kivy Texture
        buf = rgb_frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.texture = texture


# ==========================================
# 2. MAIN TRANSLATION SCREEN
# ==========================================
class SignToTextScreen(Screen):
    def __init__(self, **kwargs):
        super(SignToTextScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header Title
        header = Label(
            text="[b]SignBridge[/b] Mobile (Cyber Edition)",
            markup=True,
            font_size='22sp',
            size_hint_y=0.1,
            color=(0, 0.9, 1, 1)
        )
        layout.add_widget(header)

        # Camera Viewport
        self.camera_view = KivyCamera(size_hint_y=0.6)
        layout.add_widget(self.camera_view)

        # Translation Output Box
        self.output_label = Label(
            text="Naghihintay ng hand sign...",
            font_size='18sp',
            size_hint_y=0.15,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.output_label)

        # Action Control Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)

        btn_speak = Button(
            text="Mag-salita (TTS)",
            background_color=(0, 0.7, 0.9, 1),
            font_size='16sp'
        )
        btn_speak.bind(on_press=self.speak_output)

        btn_nav = Button(
            text="Sign Library",
            background_color=(0.3, 0.3, 0.8, 1),
            font_size='16sp'
        )
        btn_nav.bind(on_press=self.go_to_library)

        btn_layout.add_widget(btn_speak)
        btn_layout.add_widget(btn_nav)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def on_enter(self):
        self.camera_view.start_camera()

    def on_leave(self):
        self.camera_view.stop_camera()

    def speak_output(self, instance):
        text = self.output_label.text
        if tts:
            try:
                tts.speak(text)
            except Exception as e:
                print(f"[TTS Error]: {e}")
        else:
            print(f"[Mobile Speech Simulation]: {text}")

    def go_to_library(self, instance):
        self.manager.current = 'library_screen'


# ==========================================
# 3. SIGN LIBRARY SCREEN
# ==========================================
class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super(LibraryScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        header = Label(
            text="[b]Sign Library & Reference[/b]",
            markup=True,
            font_size='22sp',
            size_hint_y=0.1,
            color=(0, 0.9, 1, 1)
        )
        layout.add_widget(header)

        # Grid view para sa mga senyas/signs
        scroll = ScrollView(size_hint_y=0.75)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        sample_signs = [
            "Kumusta", "Salamat", "Mahal Kita", 
            "Tulong", "Oo", "Hindi", 
            "Magandang Umaga", "Paalam"
        ]
        
        for sign in sample_signs:
            btn = Button(
                text=sign,
                size_hint_y=None,
                height=90,
                background_color=(0.15, 0.2, 0.3, 1),
                font_size='16sp'
            )
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # Back Navigation Button
        btn_back = Button(
            text="Bumalik sa Camera",
            size_hint_y=0.15,
            background_color=(0.9, 0.2, 0.4, 1),
            font_size='16sp'
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'sign_screen'


# ==========================================
# 4. MAIN APPLICATION ENTRY POINT
# ==========================================
class SignBridgeMobileApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SignToTextScreen(name='sign_screen'))
        sm.add_widget(LibraryScreen(name='library_screen'))
        return sm


if __name__ == '__main__':
    SignBridgeMobileApp().run()