import Leap, sys, thread, time, math
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
#from pynput.mouse import Button, Controller
import pynput.mouse as ms
import pynput.keyboard as kb

class LeapMotionListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID','STATE_START', 'STATE_UPDATE','STATE_END']
    
    isPressed=0
    isPinched=0
    isConfigured=0
    configStep=1

    mouseMaxX=0
    mouseMaxY=0
    leapMinX=0
    leapMaxX=0
    leapMinY=0
    leapMaxY=0
    leapZ=0

    def on_init(self, controller):
        print "Initialized"
        raw_input("Press enter after taking mouse cursor to bottom right of screen")
        (self.mouseMaxX, self.mouseMaxY)=mouse.position
        self.mouseMaxX=self.mouseMaxX+1
        self.mouseMaxY=self.mouseMaxY+1
        print str(self.mouseMaxX) + " , " + str(self.mouseMaxY)

    def on_connect(self, controller):
        print "Connected"
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);


    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    
    def on_frame(self, controller):
        frame = controller.frame()
        if(self.isConfigured==0):
            for hand in frame.hands:
                
                if(hand.pinch_strength==0.0):
                    self.isPinched=0
                
                for finger in hand.fingers:
                    if self.finger_names[finger.type]=='Index':
                        
                        if(self.configStep==1):
                            print("Pinch at top left corner")
                            if(hand.pinch_strength==1.0 and self.isPinched==0):
                                self.leapMinX=finger.stabilized_tip_position.x
                                self.leapMaxY=finger.stabilized_tip_position.y
                                self.leapZ=finger.stabilized_tip_position.z
                                print str(self.leapMinX) + ", " + str(self.leapMaxY)
                                self.configStep=self.configStep +1
                                self.isPinched=1
                        
                        elif(self.configStep==2):
                            print("Pinch at top right corner")
                            if(hand.pinch_strength==1.0 and self.isPinched==0):
                                self.leapMaxX=finger.stabilized_tip_position.x
                                if(self.leapZ<finger.stabilized_tip_position.z):
                                    self.leapZ=finger.stabilized_tip_position.z
                                print str(self.leapMaxX)
                                self.configStep=self.configStep +1
                                self.isPinched=1
                        
                        elif(self.configStep==3):
                            print("Pinch at bottom center")
                            if(hand.pinch_strength==1.0 and self.isPinched==0):
                                self.leapMinY=finger.stabilized_tip_position.y
                                if(self.leapZ<finger.stabilized_tip_position.z):
                                    self.leapZ=finger.stabilized_tip_position.z
                                print str(self.leapMinY)
                                self.configStep=self.configStep +1
                                self.isPinched=1
                        
                        elif(self.configStep==4):
                            self.leapMinY=self.leapMinY-10
                            print str(self.leapMinX) + " - " + str(self.leapMaxX) + " , " + str(self.leapMinY) + " - " + str(self.leapMaxY) + " , " + str(self.leapZ)
                            self.isConfigured=1
            
            return

        for hand in frame.hands:
            
            handType = "Left Hand" if hand.is_left else "Right Hand"
            
            if(hand.pinch_strength==1.0 and self.isPinched==0):
                keyboard.press(kb.Key.alt)
                keyboard.press(kb.Key.space)
                keyboard.press('n')
                keyboard.release('n')
                keyboard.release(kb.Key.space)
                keyboard.release(kb.Key.alt)
                self.isPinched=1

            if(hand.pinch_strength==0.0):
                self.isPinched=0

            normal = hand.palm_normal
            direction = hand.direction

            for finger in hand.fingers:
                if self.finger_names[finger.type]=='Index':
                    xLeap=(finger.stabilized_tip_position.x * (self.mouseMaxX/2)/((self.leapMaxX - self.leapMinX)/2)) + self.mouseMaxX/2
                    yLeap=self.mouseMaxY - ((finger.stabilized_tip_position.y - self.leapMinY) * self.mouseMaxY/(self.leapMaxY - self.leapMinY))
                    mouse.position=(xLeap,yLeap)
                    
                    if(finger.stabilized_tip_position.z < self.leapZ-5 and self.isPressed==0):
                        mouse.click(ms.Button.left,1)
                        self.isPressed=1
                    elif (finger.tip_position.z > self.leapZ+5):
                        self.isPressed=0


        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                swipeDir=swipe.direction
                
                #Left/Right arrow key movement
                #if(swipeDir.x > 0 and math.fabs(swipeDir.x) > math.fabs(swipeDir.y)):
                #    print "Swiped Right" + str(swipe.id)
                #    keyboard.press(kb.Key.left)
                #    keyboard.release(kb.Key.left)
                #elif(swipeDir.x < 0 and math.fabs(swipeDir.x) > math.fabs(swipeDir.y)):
                #    print "Swiped Left"
                #    keyboard.press(kb.Key.right)
                #    keyboard.release(kb.Key.right)
                
                if(swipeDir.y > 0 and math.fabs(swipeDir.x) < math.fabs(swipeDir.y)):
                    #print "Swiped Up"
                    mouse.scroll(0,-200)
                elif(swipeDir.y < 0 and math.fabs(swipeDir.x) < math.fabs(swipeDir.y)):
                    #print "Swiped Down"
                    mouse.scroll(0,200)
                


def main():
    listener=LeapMotionListener()
    controller=Leap.Controller()
    controller.add_listener(listener)
    print "Lolwa"
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)


mouse = ms.Controller()
keyboard = kb.Controller()

if __name__=="__main__":
    main()
