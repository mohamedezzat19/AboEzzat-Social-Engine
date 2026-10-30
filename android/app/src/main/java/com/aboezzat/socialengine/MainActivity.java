package com.aboezzat.socialengine;

import android.Manifest;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.core.content.ContextCompat;
import java.security.SecureRandom;

public class MainActivity extends Activity {
 private static final String PREFS="social_engine";
 private static final int REQUEST_NOTIFICATIONS=501;
 private TextView statusView;
 private String token;

 @Override public void onCreate(Bundle state) {
  super.onCreate(state);
  token=getOrCreateToken();
  buildScreen();
  if(Build.VERSION.SDK_INT>=33 && ContextCompat.checkSelfPermission(this,Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
   requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},REQUEST_NOTIFICATIONS);
 }

 private String getOrCreateToken() {
  SharedPreferences p=getSharedPreferences(PREFS,MODE_PRIVATE);
  String old=p.getString("api_token",null);
  if(old!=null && old.length()>=64) return old;
  byte[] bytes=new byte[32]; new SecureRandom().nextBytes(bytes);
  StringBuilder s=new StringBuilder();
  for(byte b:bytes) s.append(String.format(java.util.Locale.US,"%02x",b));
  p.edit().putString("api_token",s.toString()).apply();
  return s.toString();
 }

 private void buildScreen() {
  ScrollView scroll=new ScrollView(this); scroll.setBackgroundColor(Color.rgb(13,18,30));
  LinearLayout root=new LinearLayout(this); root.setOrientation(1); root.setPadding(dp(24),dp(28),dp(24),dp(28)); scroll.addView(root);
  TextView title=label("AboEzzat Social Engine",25); title.setGravity(Gravity.CENTER); title.setTextColor(Color.WHITE); root.addView(title);
  TextView sub=label("محرك استخراج محلي يعمل على هذا الهاتف",15); sub.setGravity(Gravity.CENTER); root.addView(sub);
  statusView=label("المحرك متوقف",18); statusView.setGravity(Gravity.CENTER); statusView.setPadding(dp(12),dp(16),dp(12),dp(16)); statusView.setBackgroundColor(Color.rgb(29,42,61)); root.addView(statusView);
  Button start=button("تشغيل المحرك"); start.setOnClickListener(v->startEngine()); root.addView(start);
  Button stop=button("إيقاف المحرك"); stop.setOnClickListener(v->stopEngine()); root.addView(stop);
  root.addView(label("عنوان الاتصال المحلي",14));
  TextView endpoint=label("http://127.0.0.1:8765",15); endpoint.setTextIsSelectable(true); root.addView(endpoint);
  root.addView(label("مفتاح الربط الخاص — لا تشاركه مع أحد",14));
  TextView tokenView=label(token,13); tokenView.setTextIsSelectable(true); root.addView(tokenView);
  Button copy=button("نسخ إعدادات Share New"); copy.setOnClickListener(v->{
   String value="Base URL: http://127.0.0.1:8765\nBearer token: "+token;
   ClipboardManager cb=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
   cb.setPrimaryClip(ClipData.newPlainText("AboEzzat Social Engine",value));
   Toast.makeText(this,"تم نسخ إعدادات الربط",Toast.LENGTH_SHORT).show();
  }); root.addView(copy);
  TextView note=label("شغّل المحرك أولاً، ثم ضع العنوان والمفتاح في إعدادات Social Engine داخل Share New. اترك إشعار المحرك ظاهرًا أثناء الاستخدام.",14);
  note.setPadding(0,dp(18),0,0); root.addView(note);
  setContentView(scroll); refreshStatus();
 }

 private TextView label(String text,int size) {
  TextView v=new TextView(this); v.setText(text); v.setTextColor(Color.rgb(220,228,240)); v.setTextSize(size); v.setPadding(dp(4),dp(10),dp(4),dp(8)); return v;
 }
 private Button button(String text) {
  Button b=new Button(this); b.setText(text); b.setAllCaps(false);
  LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.setMargins(0,dp(7),0,dp(7)); b.setLayoutParams(lp); return b;
 }
 private void startEngine() {
  Intent i=new Intent(this,EngineService.class);
  if(Build.VERSION.SDK_INT>=26) ContextCompat.startForegroundService(this,i); else startService(i);
  statusView.setText("جاري تشغيل المحرك..."); statusView.setTextColor(Color.YELLOW);
 }
 private void stopEngine() {
  stopService(new Intent(this,EngineService.class)); statusView.setText("المحرك متوقف"); statusView.setTextColor(Color.LTGRAY);
 }
 private void refreshStatus() {
  boolean running=getSharedPreferences(PREFS,MODE_PRIVATE).getBoolean("running",false);
  statusView.setText(running?"المحرك يعمل — جاهز لاستقبال طلبات Share New":"المحرك متوقف");
  statusView.setTextColor(running?Color.rgb(91,220,145):Color.LTGRAY);
 }
 private int dp(int n) { return (int)(n*getResources().getDisplayMetrics().density+0.5f); }
 @Override protected void onResume() { super.onResume(); if(statusView!=null) refreshStatus(); }
}
