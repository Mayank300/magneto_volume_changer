import cv2
import numpy as np
import subprocess

def set_volume(volume_level):
    # Ensure the volume is between 0 and 100
    volume_level = max(0, min(100, volume_level))
    
    # Use AppleScript to adjust the volume
    script = f"osascript -e 'set volume output volume {volume_level}'"
    subprocess.run(script, shell=True)

def track_color_and_control_volume():
    # Start the webcam
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break
        
        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define the range for the red color (you can modify this range for other colors)
        # Lower and upper bounds for the color red in HSV space
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        
        # Create a mask for red color
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Also consider the second range of red (due to the wraparound in the hue channel)
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        # Combine the two masks to get the final red mask
        mask = cv2.bitwise_or(mask, mask2)
        
        # Bitwise-AND the mask and the frame to extract the red object
        red_objects = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Find contours in the mask (the red objects)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (the detected red object)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get the bounding box of the largest contour
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Draw a rectangle around the red object
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
            
            # Calculate the area of the bounding box
            area = w * h
            
            # Map the area to a volume level (volume range: 0 - 100)
            # You may need to adjust the area-to-volume mapping based on your camera's resolution and your preferences
            volume_level = np.interp(area, [1000, 10000], [0, 100])  # Map the area to volume (adjust the range as needed)
            print(volume_level)
            # Set the system volume based on the object size
            set_volume(volume_level)
        
        # Display the frame with the detected red object and volume control
        cv2.imshow("Color Tracking with Volume Control", frame)
        
        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    track_color_and_control_volume()
