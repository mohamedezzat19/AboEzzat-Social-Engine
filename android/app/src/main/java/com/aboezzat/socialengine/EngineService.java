package com.aboezzat.socialengine;

import android.app.*;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.*;
import androidx.core.app.NotificationCompat;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;
import fi.iki.elonen.NanoHTTPD;

public class EngineService extends Service {
 private static final String PREFS="social_engine", CHANNEL="social_engine_running";
 private static final int NOTIFICATION=853, PORT=8765;
 private LocalApiServer server;

 @Override public void onCreate() {
  super.onCreate(); createChannel();
  Notification n=new NotificationCompat.Builder(this,CHANNEL)
   .setSmallIcon(android.R.drawable.stat_sys_upload)
   .setContentTitle("AboEzzat Social Engine")
   .setContentText("محرك الاستخراج يعمل على الهاتف")
   .setOngoing(true).setPriority(NotificationCompat.PRIORITY_LOW).build();
  if(Build.VERSION.SDK_INT>=34) startForeground(NOTIFICATION,n,ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
  else startForeground(NOTIFICATION,n);
  startLocalServer();
 }

 private void startLocalServer() {
  new Thread(()->{
   try {
    if(!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
    server=new LocalApiServer();
    server.start(NanoHTTPD.SOCKET_READ_TIMEOUT,false);
    getSharedPreferences(PREFS,MODE_PRIVATE).edit().putBoolean("running",true).apply();
   } catch(Exception e) {
    getSharedPreferences(PREFS,MODE_PRIVATE).edit().putBoolean("running",false).apply();
    stopSelf();
   }
  },"SocialEngineStartup").start();
 }

 @Override public int onStartCommand(Intent i,int flags,int id) { return START_STICKY; }
 @Override public void onDestroy() {
  if(server!=null) server.stop();
  getSharedPreferences(PREFS,MODE_PRIVATE).edit().putBoolean("running",false).apply();
  stopForeground(STOP_FOREGROUND_REMOVE); super.onDestroy();
 }
 @Override public IBinder onBind(Intent i) { return null; }

 private void createChannel() {
  if(Build.VERSION.SDK_INT>=26) {
   NotificationChannel c=new NotificationChannel(CHANNEL,"Social Engine",NotificationManager.IMPORTANCE_LOW);
   c.setDescription("حالة تشغيل محرك الاستخراج المحلي");
   getSystemService(NotificationManager.class).createNotificationChannel(c);
  }
 }

 private final class LocalApiServer extends NanoHTTPD {
  LocalApiServer() { super("127.0.0.1",PORT); }
  @Override public Response serve(IHTTPSession s) {
   String path=s.getUri();
   if("/health".equals(path)&&Method.GET.equals(s.getMethod()))
    return json(Response.Status.OK,"{\"status\":\"ok\",\"service\":\"AboEzzat Social Engine\",\"runtime\":\"android\"}");
   if(!"/api/v1/extract".equals(path)||!Method.POST.equals(s.getMethod()))
    return json(Response.Status.NOT_FOUND,"{\"detail\":\"Not found\"}");
   String expected=getSharedPreferences(PREFS,MODE_PRIVATE).getString("api_token","");
   if(!validBearer(s.getHeaders().get("authorization"),expected))
    return json(Response.Status.UNAUTHORIZED,"{\"detail\":\"Bearer token required\"}");
   try {
    Map<String,String> files=new HashMap<>(); s.parseBody(files);
    String raw=files.get("postData");
    if(raw==null||raw.length()>65536) return json(Response.Status.BAD_REQUEST,"{\"detail\":\"Invalid request body\"}");
    JSONObject payload=new JSONObject(raw);
    String url=payload.optString("url","").trim(), cookies=payload.optString("cookies","");
    if(url.isEmpty()||url.length()>4096||cookies.length()>16384||cookies.contains("\r")||cookies.contains("\n"))
     return json(Response.Status.BAD_REQUEST,"{\"detail\":\"Invalid request payload\"}");
    String result=Python.getInstance().getModule("social_engine").callAttr("extract_json",url,cookies).toString();
    return json(Response.Status.OK,result);
   } catch(Exception e) {
    return json(Response.Status.INTERNAL_ERROR,"{\"success\":false,\"error_code\":\"ENGINE_ERROR\",\"message\":\"Extraction service error\",\"formats\":[]}");
   }
  }
  private boolean validBearer(String header,String expected) {
   if(header==null||!header.startsWith("Bearer ")||expected==null||expected.length()<64) return false;
   return MessageDigest.isEqual(header.substring(7).trim().getBytes(StandardCharsets.UTF_8),expected.getBytes(StandardCharsets.UTF_8));
  }
  private Response json(Response.Status status,String body) {
   Response r=newFixedLengthResponse(status,"application/json; charset=utf-8",body);
   r.addHeader("Cache-Control","no-store"); return r;
  }
 }
}
