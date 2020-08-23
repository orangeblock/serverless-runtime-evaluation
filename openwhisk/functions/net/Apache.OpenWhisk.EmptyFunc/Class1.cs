using System;
using Newtonsoft.Json.Linq;

namespace Apache.OpenWhisk.EmptyFunc
{
    public class Class1
    {
        public JObject Main(JObject args)
        {
            JObject response = new JObject();
            response.Add("status", new JValue(200));
            return (response);
        }
    }
}
