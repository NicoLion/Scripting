import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import ddf.minim.*; 
import ddf.minim.analysis.*; 
import ddf.minim.effects.*; 
import ddf.minim.signals.*; 
import ddf.minim.spi.*; 
import ddf.minim.ugens.*; 
import processing.sound.*; 
import processing.pdf.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class Sound_of_Wind_v_4 extends PApplet {









SoundFile file;
Minim minim; // intance of the minim library with I call minim
AudioPlayer soundofwind;
Table table;
float[] scaledPower;
int a = 50;  //initialize
int b = 300; //initialize
float min = -146.79f; //minimum power output recorded in the raw data
float max = 11434; // maximun power output recorded in raw data
float x = 0;
int   k = 0;
 
 public void setup()
{
  
  background(255, 255, 255);
  stroke(0);
  frameRate(120);
  minim =new Minim(this);
  soundofwind = minim.loadFile("sevenctfortwo.wav");     
}

public void draw() 
{
  Table table = loadTable("callahandemo.csv", "header");// load table
   String [] sum = table.getStringColumn(3);
   float [] suma = new float[sum.length]; // float vector of the lenght sum 
   for( int i= 0; i< suma.length; i++) {   
     suma[i]= PApplet.parseFloat(sum[i]); // assignn values from the sum vector (string) into float form and vector suma
     }
   float [] scaledPower = new float[suma.length];// create a new vector that will fit into the screen values dispersed
   for( int i= 0; i< suma.length; i++){
     scaledPower[i]= a + (suma[i]-min) *(b-a)/(max-min); //scaling operation
     }
   println(scaledPower);
    
     k ++ ;
     x ++;
     
     if(x<width){
     point(x,scaledPower[k]);
     }
     else if (x>=width && k<=scaledPower.length && x<=scaledPower.length){
     point(x-width,scaledPower[k]);  
     }
     else
     {
     stop();
     }
   }
   
  
public void mousePressed()
{
  soundofwind.play();
}

public void stop() {
  minim.stop();
  super.stop();
}
  public void settings() {  size(1000, 500); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "Sound_of_Wind_v_4" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
