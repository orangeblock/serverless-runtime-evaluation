<?php
function handler($context){
    $response = $context["response"];
    $response->getBody()->write("{\"status\": 200}");
}
