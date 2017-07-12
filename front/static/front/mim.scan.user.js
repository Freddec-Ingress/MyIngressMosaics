// ==UserScript==
// @id             iitc-myingressmosaics@freddec
// @name           MyIngressMosaics IITC plugin
// @version        0.0.0
// @include        https://*.ingress.com/intel*
// @include        http://*.ingress.com/intel*
// @match          https://*.ingress.com/intel*
// @match          http://*.ingress.com/intel*
// @include        https://*.ingress.com/mission/*
// @include        http://*.ingress.com/mission/*
// @match          https://*.ingress.com/mission/*
// @match          http://*.ingress.com/mission/*
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
// Retrieve Ninatic version

var NIANTIC_CURRENT_VERSION = null;

var reVersion = new RegExp('"X-CSRFToken".*[a-z].v="([a-f0-9]{40})";');

var minified = new RegExp('^[a-zA-Z$][a-zA-Z$0-9]?$');

for (var topLevel in window) {

    if (minified.test(topLevel)) {

        var topObject = window[topLevel];
        if (topObject && topObject.prototype) {

            for (var secLevel in topObject.prototype) {

                if (minified.test(secLevel)) {

                    var item = topObject.prototype[secLevel];
                    if (item && typeof(item) == "function") {

                        var funcStr = item.toString();

                        var match = reVersion.exec(funcStr);
                        if (match) {
                            NIANTIC_CURRENT_VERSION = match[1];
                        }
                    }
                }
            }
        }
    }
}

//--------------------------------------------------------------------------------------------------
// Function to read cookie

function readCookie(name) {

    var C, i, c = document.cookie.split('; ');

    var cookies = {};
    for (i = c.length - 1; i >= 0; i--) {
        C = c[i].split('=');
        cookies[C[0]] = unescape(C[1]);
    }

    return cookies[name];
}

//--------------------------------------------------------------------------------------------------
// Function to call Ingress API

function callIngressAPI(action, data, successCallback, errorCallback) {

    var post_data = JSON.stringify($.extend({}, data, {v: NIANTIC_CURRENT_VERSION}));

    var onError = function(jqXHR, textStatus, errorThrown) {

        if (errorCallback) {
            errorCallback(jqXHR, textStatus, errorThrown);
        }
    };

    var onSuccess = function(data, textStatus, jqXHR) {

        if (data && data.error && data.error == 'out of date') {

            if (errorCallback) {
                errorCallback(jqXHR, textStatus, "data.error == 'out of date'");
            }

        } else {

            successCallback(data, textStatus, jqXHR);
        }
    };

    var result = $.ajax({
        url: '/r/'+action,
        type: 'POST',
        data: post_data,
        context: data,
        dataType: 'json',
        success: [onSuccess],
        error: [onError],
        contentType: 'application/json; charset=utf-8',
        beforeSend: function(req) {
            req.setRequestHeader('X-CSRFToken', readCookie('csrftoken'));
        }
    });

    result.action = action;

    return result;
}

//--------------------------------------------------------------------------------------------------
// Function to call MyIngressMosaics API

function callMIMAPI(action, data) {

    var post_data = data;
    post_data.push('FredDeco');

    var result = $.ajax("https://www.myingressmosaics.com/api/ext_register/", {
        type: 'POST',
        data: JSON.stringify(post_data),
        dataType: 'json',
    });

    result.action = action;

    return result;
}

//--------------------------------------------------------------------------------------------------
// Functions to process tile request and tile data

var tilesProcessed = [];
var tilesToBeProcessed = [];

function processTileData(data) {

    for (var item of data) {
        if (item[2][0] == 'p' && item[2][10] === true) {

            var portal_id = item[0];

            if (portalsProcessed.indexOf(portal_id) == -1 && portalsToBeProcessed.indexOf(portal_id) == -1) {
                portalsToBeProcessed.push(portal_id);
            }
        }
    }
}

function handleTileResponse(data, textStatus, jqXHR) {

    if (data && data.result) {
        for (var tile_id in data.result.map) {

            var val = data.result.map[tile_id];
            if ('error' in val) {
            }
            else {

                processTileData(val.gameEntities);

                tilesProcessed.push(tile_id);
                tilesToBeProcessed.splice(tilesToBeProcessed.indexOf(tile_id), 1);
            }
        }
    }
}

function processTileRequest() {

    if (tilesToBeProcessed.length > 0) {

        var data = { tileKeys: tilesToBeProcessed.slice(0, 12) };
        callIngressAPI('getEntities', data, handleTileResponse);
    }
}

//--------------------------------------------------------------------------------------------------
// Functions to process portal request and portal data

var portalsProcessed = [];
var portalsToBeProcessed = [];

function processPortalRequest() {

    if (portalsToBeProcessed.length > 0) {

        var portal_id = portalsToBeProcessed[0];

        portalsToBeProcessed.splice(portalsToBeProcessed.indexOf(portal_id), 1);

        var data = { guid: portal_id };
        callIngressAPI('getTopMissionsForPortal', data, function(data, textStatus, jqXHR) {

            if (data && data.result) {

                portalsProcessed.push(portal_id);

                for (var item of data.result) {

                    var mission_name = item[1];

                    var found = mission_name.match(/[0-9]+/);
                    if (found) {

                        console.log('Mission found: %s', mission_name);

                        var mission_id = item[0];

                        if (missionsProcessed.indexOf(mission_id) == -1 && missionsToBeProcessed.indexOf(mission_id) == -1) {
                            missionsToBeProcessed.push(mission_id);
                        }
                    }
                }
            }

            processPortalRequest();
        });
    }
}

//--------------------------------------------------------------------------------------------------
// Functions to process mission request and mission data

var missionsProcessed = [];
var missionsToBeProcessed = [];

function processMissionRequest() {

    if (missionsToBeProcessed.length > 0) {

        var mission_id = missionsToBeProcessed[0];

        missionsToBeProcessed.splice(missionsToBeProcessed.indexOf(mission_id), 1);

        var data = { guid: mission_id };
        callIngressAPI('getMissionDetails', data, function(data, textStatus, jqXHR) {

            if (data && data.result) {

                missionsProcessed.push(mission_id);

                callMIMAPI('ext_register', data.result);
            }

            processMissionRequest();
        });
    }
}

//--------------------------------------------------------------------------------------------------
// Implement our script

function ourScript() {

    // Build map
    var map = new google.maps.Map(document.getElementById('map_canvas'), {

        zoom: MAP_PARAMS.zoom,
        zoomControl: true,
        disableDefaultUI: true,
        center: {lat: MAP_PARAMS.lat, lng: MAP_PARAMS.lng},
    });

    setInterval(processTileRequest, 2500);
    setInterval(processPortalRequest, 2500);
    setInterval(processMissionRequest, 2500);

    // Add tile to be processed when map moves
    map.addListener('idle', function(e) {

        var bds = map.getBounds();

        var west = bds.getSouthWest().lng();
        var east = bds.getNorthEast().lng();
        var north = bds.getNorthEast().lat();
        var south = bds.getSouthWest().lat();

        var zoom = 15;
        var minLevel = 0;
        var tilesPerEdge = 32000;

        var xStart = Math.floor((west + 180) / 360 * tilesPerEdge);
        var xEnd = Math.floor((east + 180) / 360 * tilesPerEdge);

        var yStart = Math.floor((1 - Math.log(Math.tan(north * Math.PI / 180) + 1 / Math.cos(north * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);
        var yEnd = Math.floor((1 - Math.log(Math.tan(south * Math.PI / 180) + 1 / Math.cos(south * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);

        // Tiles
        for (var x = xStart; x <= xEnd; x++) {
            for (var y = yStart; y <= yEnd; y++) {

                var tile_id = zoom + "_" + x + "_" + y + "_" + minLevel + "_8_100";
                tilesToBeProcessed.push(tile_id);
           }
        }
    });
}

//--------------------------------------------------------------------------------------------------
// Load our script

var script = document.createElement('script');
script.appendChild(document.createTextNode('('+ ourScript +');'));
(document.body || document.head || document.documentElement).appendChild(script);

//--------------------------------------------------------------------------------------------------
// Execute our script

window.onload = ourScript;
document.body.onload = ourScript;
