// ==UserScript==
// @name           IM Country Hacking plugin
// @version        1.0.0
// @include        https://ingressmosaik.com
// @match          https://ingressmosaik.com
// @downloadURL    https://www.myingressmosaics.com/static/front/mim.country.hack.user.js
// @grant          none
// ==/UserScript==

function callMIMAPI(action, data, successCallback, errorCallback) {

    var onError = function(jqXHR, textStatus, errorThrown) {

        if (errorCallback) {
            errorCallback(jqXHR, textStatus, errorThrown);
        }
    };

    var onSuccess = function(data, textStatus, jqXHR) {

        if (successCallback) {
            successCallback(data, textStatus, jqXHR);
        }
    };

    var result = $.ajax("https://www.myingressmosaics.com/api/" + action, {
        type: 'POST',
        data: JSON.stringify(data),
        dataType: 'json',
        success: [onSuccess],
        error: [onError],
        contentType: 'application/json; charset=utf-8',
    });

    result.action = action;

    return result;
}

var head = document.getElementsByTagName('head')[0] || document.documentElement;

var script = document.createElement('script');
script.type = 'text/javascript';
script.src = '//ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js';

head.insertBefore(script, head.firstChild);

function init() {

    $('#land a div').each(function() {

        var country_name = $(this).clone().children().remove().end().text().trim();
        console.log(country_name);

        var mosaic_count = $(this).children('span').first().text().trim();
        console.log(mosaic_count);

        var data = { 'country_name':country_name, 'mosaic_count':mosaic_count };
        callMIMAPI('im/country', data);
    });
}

var script = document.createElement('script');
script.appendChild(document.createTextNode('(' + init + ');'));
(document.body || document.head || document.documentElement).appendChild(script);

window.onload = init;
document.body.onload = init;