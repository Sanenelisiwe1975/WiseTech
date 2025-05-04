import cv2
import mediapipe as mp
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
from azure.iot.hub import IoTHubRegistryManager
from azure.communication.sms import SmsClient
import time

# ============================
# CONFIGURATION (Replace with your Azure keys)
# ============================
SPEECH_KEY = "YOUR_AZURE_SPEECH_KEY"
SPEECH_REGION = "eastus"  # Change to your region
IOT_HUB_CONN_STR = "YOUR_IOT_HUB_CONNECTION_STRING"
SMS_CONN_STR = "YOUR_COMMUNICATION_SERVICES_CONN_STRING"
CAREGIVER_PHONE = "0737139866"  # Caregiver's phone number
YOUR_PHONE = "0601313605"      # Your provisioned SMS number

# ============================
# INITIALIZE SERVICES
# ============================
class WiseTech:
    def __init__(self):
        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize cooldown timers
        self.last_command_time = 0
        self.command_cooldown = 2  # seconds
        
        # Azure Services
        self.initialize_azure_services()
        
        # Gesture thresholds (customizable)
        self.gesture_thresholds = {
            'mouth_open': 0.03,
            'eye_closed': 0.7,
            'eyebrow_raise': 0.15
        }
        
        # Command mappings
        self.commands = {
            'double_blink': 'TOGGLE_LIGHTS',
            'mouth_open': 'EMERGENCY_ALERT',
            'eyebrow_raise': 'NEXT_ITEM',
            'head_left': 'SCROLL_LEFT',
            'head_right': 'SCROLL_RIGHT'
        }
        
        self.speak("Wise Tech initialized. Ready for commands.")

    def initialize_azure_services(self):
        """Initialize all Azure cloud services"""
        try:
            # Azure Speech Service
            self.speech_config = SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
            self.speech_synthesizer = SpeechSynthesizer(speech_config=self.speech_config)
            
            # Azure IoT Hub
            self.iot_registry = IoTHubRegistryManager(IOT_HUB_CONN_STR) if IOT_HUB_CONN_STR else None
            
            # Azure SMS
            self.sms_client = SmsClient.from_connection_string(SMS_CONN_STR) if SMS_CONN_STR else None
            
        except Exception as e:
            print(f"Azure services initialization failed: {str(e)}")
            raise

    # ============================
    # ENHANCED GESTURE DETECTION
    # ============================
    def detect_gestures(self, frame):
        """Advanced gesture detection with multiple features"""
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Mouth openness (smile detection)
        mouth_open = (landmarks[13].y - landmarks[14].y) > self.gesture_thresholds['mouth_open']
        
        # Eye blink detection
        left_eye_closed = (landmarks[159].y - landmarks[145].y) < self.gesture_thresholds['eye_closed']
        right_eye_closed = (landmarks[386].y - landmarks[374].y) < self.gesture_thresholds['eye_closed']
        
        # Eyebrow raise detection
        left_eyebrow_raise = (landmarks[70].y - landmarks[63].y) > self.gesture_thresholds['eyebrow_raise']
        right_eyebrow_raise = (landmarks[300].y - landmarks[293].y) > self.gesture_thresholds['eyebrow_raise']
        
        # Head pose estimation
        nose_tip = landmarks[4]
        head_tilt = "left" if nose_tip.x < 0.4 else "right" if nose_tip.x > 0.6 else "center"
        
        return {
            'mouth_open': mouth_open,
            'left_eye_closed': left_eye_closed,
            'right_eye_closed': right_eye_closed,
            'left_eyebrow_raise': left_eyebrow_raise,
            'right_eyebrow_raise': right_eyebrow_raise,
            'head_tilt': head_tilt,
            'landmarks': landmarks
        }

    # ============================
    # INTELLIGENT ACTION SYSTEM
    # ============================
    def execute_command(self, command_type):
        """Handle different types of commands with cooldown"""
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return
            
        self.last_command_time = current_time
        
        if command_type == "EMERGENCY_ALERT":
            self.send_emergency_alert()
        elif command_type == "TOGGLE_LIGHTS":
            self.handle_iot_command("LIGHTS_TOGGLE")
        elif command_type == "NEXT_ITEM":
            self.handle_ui_command("SELECT_NEXT")
        elif command_type == "SCROLL_LEFT":
            self.handle_ui_command("SCROLL_LEFT")
        elif command_type == "SCROLL_RIGHT":
            self.handle_ui_command("SCROLL_RIGHT")

    def handle_iot_command(self, command):
        """Smart home device control"""
        if self.iot_registry:
            try:
                self.iot_registry.send_c2d_message("wisetech_device", command)
                self.speak(f"Command {command.replace('_', ' ')} executed")
            except Exception as e:
                print(f"IoT Error: {str(e)}")

    def handle_ui_command(self, command):
        """For controlling UI elements"""
        print(f"UI Command: {command}")
        self.speak(f"Navigating {command.replace('_', ' ')}")

    def send_emergency_alert(self):
        """Enhanced emergency response"""
        if self.sms_client:
            try:
                self.sms_client.send(
                    from_=YOUR_PHONE,
                    to=CAREGIVER_PHONE,
                    message="URGENT: WiseTech user needs immediate assistance!"
                )
                self.speak("Emergency alert sent to your contacts")
            except Exception as e:
                print(f"SMS Error: {str(e)}")

    def speak(self, text):
        """Natural sounding speech output"""
        try:
            self.speech_synthesizer.speak_text_async(text).get()
        except Exception as e:
            print(f"Speech Error: {str(e)}")

    # ============================
    # MAIN APPLICATION LOOP
    # ============================
    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("WiseTech System Active - Press 'q' to quit")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Mirror frame for user-friendly interaction
            frame = cv2.flip(frame, 1)
            
            # Detect gestures
            gestures = self.detect_gestures(frame)
            
            if gestures:
                # Visual feedback
                self.draw_gesture_feedback(frame, gestures)
                
                # Command processing
                self.process_gestures(gestures)
            
            # Display frame
            cv2.imshow('WiseTech Assistive System', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.speak("WiseTech system shutting down")

    def draw_gesture_feedback(self, frame, gestures):
        """Visual feedback for detected gestures"""
        if gestures['mouth_open']:
            cv2.putText(frame, "EMERGENCY MODE", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if gestures['left_eye_closed'] and gestures['right_eye_closed']:
            cv2.putText(frame, "LIGHT CONTROL", (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if gestures['left_eyebrow_raise'] or gestures['right_eyebrow_raise']:
            cv2.putText(frame, "NAVIGATION", (50, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        if gestures['head_tilt'] != "center":
            cv2.putText(frame, f"HEAD TILT: {gestures['head_tilt'].upper()}", (50, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    def process_gestures(self, gestures):
        """Smart gesture interpretation"""
        # Emergency detection
        if gestures['mouth_open']:
            self.execute_command("EMERGENCY_ALERT")
        
        # Double blink detection
        if gestures['left_eye_closed'] and gestures['right_eye_closed']:
            self.execute_command("TOGGLE_LIGHTS")
        
        # Eyebrow raise (single side for accessibility)
        if gestures['left_eyebrow_raise'] or gestures['right_eyebrow_raise']:
            self.execute_command("NEXT_ITEM")
        
        # Head tilt navigation
        if gestures['head_tilt'] == "left":
            self.execute_command("SCROLL_LEFT")
        elif gestures['head_tilt'] == "right":
            self.execute_command("SCROLL_RIGHT")

# ============================
# ENTRY POINT
# ============================
if __name__ == "__main__":
    try:
        print("Starting WiseTech Assistive System...")
        assistive_system = WiseTech()
        assistive_system.run()
    except KeyboardInterrupt:
        print("\nSystem shutdown initiated")
    except Exception as e:
        print(f"System Error: {str(e)}")