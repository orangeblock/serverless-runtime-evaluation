import com.google.gson.JsonObject;

public class test {
  public static JsonObject main(JsonObject args){
    JsonObject response = new JsonObject();
    response.addProperty("status", 200);
    return response;
  }
}
