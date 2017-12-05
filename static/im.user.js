// ==UserScript==
// @id             myingressmosaics@freddec
// @name           IM plugin
// @version        1.0.0
// @match          https://ingressmosaik.com/de/*t=ort
// @grant          none
// ==/UserScript==

var head = document.getElementsByTagName('head')[0] || document.documentElement;

//--------------------------------------------------------------------------------------------------
// Load jQuerys

var script = document.createElement('script');
script.type = 'text/javascript';
script.src = '//ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js';

head.insertBefore(script, head.firstChild);

//--------------------------------------------------------------------------------------------------
// Our script

function init() {

    $('#site_content h4.panel-title-1').each(function(index){

        console.log('\t' + $(this).text());
    });
}

//--------------------------------------------------------------------------------------------------
// Load our script

var script = document.createElement('script');
script.appendChild(document.createTextNode('(' + init + ');'));
(document.body || document.head || document.documentElement).appendChild(script);

//--------------------------------------------------------------------------------------------------
// Execute our script

window.onload = init;
document.body.onload = init;
