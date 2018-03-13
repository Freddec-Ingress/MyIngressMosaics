// ==UserScript==
// @name           IM City Hacking plugin
// @version        1.0.0
// @include        https://ingressmosaik.com/*/*&t=ort
// @match          https://ingressmosaik.com/*/*&t=ort
// @downloadURL    https://www.myingressmosaics.com/static/front/mim.city.hack.user.js
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

    var text = $('.container-fluid .col-xs-12:nth-child(3)').children('.panel-heading-1').text().trim().split('|');

    var country_name = text[1].trim();
    console.log(country_name);

    var region_name = text[2].split('    ')[0].trim();
    console.log(region_name);

    $('#site_content .row > .col-xs-12').each(function() {

        var city_name = $(this).text().trim().split('    ')[0].trim();
        console.log(city_name);

        var mosaic_count = $(this).children('.panel-body-1').children('article').length;
        console.log(mosaic_count);

        var data = { 'country_name':country_name, 'region_name':region_name, 'city_name':city_name, 'mosaic_count':mosaic_count };
        callMIMAPI('im/city', data);
    });
}

var script = document.createElement('script');
script.appendChild(document.createTextNode('(' + init + ');'));
(document.body || document.head || document.documentElement).appendChild(script);

window.onload = init;
document.body.onload = init;
