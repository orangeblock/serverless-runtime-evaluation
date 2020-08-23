using System;
using Fission.DotNetCore.Api;

public class FissionFunction {
    public string Execute(FissionContext context) {
        return "{\"status\": 200}";
    }
}
