// ==UserScript==
// @id             myingressmosaics@freddec
// @name           MyIngressMosaics Scanning plugin
// @version        1.0.3
// @include        https://*.ingress.com/intel*
// @include        http://*.ingress.com/intel*
// @match          https://*.ingress.com/intel*
// @match          http://*.ingress.com/intel*
// @include        https://*.ingress.com/mission/*
// @include        http://*.ingress.com/mission/*
// @match          https://*.ingress.com/mission/*
// @match          http://*.ingress.com/mission/*
// @downloadURL    https://www.myingressmosaics.com/static/front/mim.scan.user.js
// @grant          none
// ==/UserScript==

var head = document.getElementsByTagName('head')[0] || document.documentElement;

//--------------------------------------------------------------------------------------------------
// Styles

head.innerHTML += '<style>' +
    '@-webkit-keyframes rotating {' +
    '	from { transform: rotate(0deg); }' +
    '   to { transform: rotate(360deg); }' +
    '}' +
    '@keyframes rotating {' +
    '	from { transform: rotate(0deg); }' +
    '	to { transform: rotate(360deg); }' +
    '}' +
    '#header {display:none;}' +
    '#geotools {right: -2px;}' +
    '#tm_button {display:none;}' +
    '#portal_filter_header {display:none;}' +
    '#game_stats {display:none;}' +
    '#loading_data_circle {display:none; animation: rotating 2s linear infinite;}' +
    '#loading_msg_text {display:none;}' +
    '#loading_msg {display:block!important;}' +
    '#dashboard_container {top:50px!important;}' +
    '#tm_start {padding: 0 5px; position: absolute; bottom: -45px; right: 0px;}' +
    '#tm_stop {padding: 0 5px; position: absolute; bottom: -45px; right: 110px;}' +
'</style>';

//--------------------------------------------------------------------------------------------------
// HTML updates

document.getElementById('dashboard_container').innerHTML +=
    '<div id="tm_start" class="unselectable bottom_right_tab_button" onclick="startScanning();">' +
    '       Start' +
    '</div>';

document.getElementById('dashboard_container').innerHTML +=
    '<div id="tm_stop" class="unselectable bottom_right_tab_button" onclick="stopScanning();">' +
    '       Stop' +
    '</div>';

document.getElementById('loading_msg_text').innerHTML = 'Scanning Data...';

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

var username = window.PLAYER.nickname;

function callMIMAPI(action, data) {

    var post_data = data;
    post_data.push(username);

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

var currentProcessed_count = 0;
var currentToBeProcessed_count = 0;

function processTileRequest() {

    if (tilesToBeProcessed.length > 0) {

        var text = '' + currentProcessed_count + '/' + currentToBeProcessed_count;
        document.getElementById('loading_msg_text').innerHTML = 'Scanning Data... ' + text;

        var tiles = tilesToBeProcessed.slice(0, 12);

        var data = { tileKeys: [] };

        for (var tile of tiles) {

            data.tileKeys.push(tile.id);
        }

        callIngressAPI('getEntities', data, function(data, textStatus, jqXHR) {

            if (data && data.result) {

                for (var tile_id in data.result.map) {

                    var val = data.result.map[tile_id];
                    if ('error' in val) {
                    }
                    else {

                        var tile = null;
                        for (var t of tiles) {
                            if (t.id == tile_id) {
                                tile = t;
                            }
                        }

                        var rectangle = new google.maps.Rectangle({
                            strokeColor: '#FF0000',
                            strokeOpacity: 0.5,
                            strokeWeight: 1,
                            fillColor: '#FF0000',
                            fillOpacity: 0.25,
                            map: M,
                            bounds: {
                                north: tile.north,
                                south: tile.south,
                                east: tile.east,
                                west: tile.west
                            }
                        });

                        currentProcessed_count += 1;

                        tilesToBeProcessed.splice(tilesToBeProcessed.indexOf(tile), 1);
                        tilesProcessed.push(tile);

                        for (var item of val.gameEntities) {
                            if (item[2][0] == 'p' && item[2][10] === true) {

                                var portal = {
                                    'id': item[0],
                                    'lat': item[2][2] / 1000000.0,
                                    'lng': item[2][3] / 1000000.0,
                                };

                                if (portalsToBeProcessed.indexOf(portal) == -1) {
                                    portalsToBeProcessed.push(portal);
                                }
                            }
                        }

                        processPortalRequest();
                    }
                }

                if (scanning) { processTileRequest(); }
            }
        });
    }
    else {

        currentProcessed_count = 0;
        currentToBeProcessed_count = 0;

        scanning = false;

        $('#loading_msg_text').hide();
        $('#loading_data_circle').hide();
    }
}

//--------------------------------------------------------------------------------------------------
// Functions to process portal request and portal data

var portalsToBeProcessed = [];

var mImage = {
    url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/enl_lev8.png',
    scaledSize: new google.maps.Size(25, 25),
};

function processPortalRequest() {

    if (portalsToBeProcessed.length > 0) {

        var portal = portalsToBeProcessed[0];

        portalsToBeProcessed.splice(portalsToBeProcessed.indexOf(portal), 1);

        var data = { guid: portal.id };
        callIngressAPI('getTopMissionsForPortal', data, function(data, textStatus, jqXHR) {

            if (data && data.result) {

                for (var item of data.result) {

                    var mission_name = item[1];

                    var found = mission_name.match(/[0-9]+/);
                    if (found) {

                        console.log(mission_name);

                        var marker = new google.maps.Marker({
                            position: {lat: portal.lat, lng: portal.lng},
                            map: M,
                            icon: mImage,
                        });

                        var mission_id = item[0];

                        if (missionsToBeProcessed.indexOf(mission_id) == -1) {
                            missionsToBeProcessed.push(mission_id);
                        }
                    }
                }

                processMissionRequest();
            }

        });
    }
}

//--------------------------------------------------------------------------------------------------
// Functions to process mission request and mission data

var missionsToBeProcessed = [];

function processMissionRequest() {

    if (missionsToBeProcessed.length > 0) {

        var mission_id = missionsToBeProcessed[0];

        missionsToBeProcessed.splice(missionsToBeProcessed.indexOf(mission_id), 1);

        var data = { guid: mission_id };
        callIngressAPI('getMissionDetails', data, function(data, textStatus, jqXHR) {

            if (data && data.result) {

                callMIMAPI('ext_register', data.result);
                processMissionRequest();
            }
        });
    }
    else {

        processPortalRequest();
    }
}

//--------------------------------------------------------------------------------------------------
// Toolbox for lat/lng computing

function tileToLat(y, tilesPerEdge) {

    var n = Math.PI - 2 * Math.PI * y / tilesPerEdge;
    return 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)));
}

function tileToLng(x, tilesPerEdge) {

    return x / tilesPerEdge * 360 - 180;
}

//--------------------------------------------------------------------------------------------------
// Initialize our script

var map = null;

var scanning = false;

function testTile(element, index, array) {

    return element.id == this.id;
}

function init() {

	var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];

    // Build map
    M = new google.maps.Map(document.getElementById('map_canvas'), {

        zoom: MAP_PARAMS.zoom,
        styles : style,
        zoomControl: true,
        disableDefaultUI: true,
        center: {lat: MAP_PARAMS.lat, lng: MAP_PARAMS.lng},
    });

    // Scanning functions
    window.startScanning = function() {

        if (scanning === true) return;

        tilesToBeProcessed = [];
        portalsToBeProcessed = [];
        missionsToBeProcessed = [];

        var bds = M.getBounds();

        var west = bds.getSouthWest().lng();
        var east = bds.getNorthEast().lng();
        var north = bds.getNorthEast().lat();
        var south = bds.getSouthWest().lat();

        var zoom = 17;
        var minLevel = 0;
        var tilesPerEdge = 32000;

        var xStart = Math.floor((west + 180) / 360 * tilesPerEdge);
        var xEnd = Math.floor((east + 180) / 360 * tilesPerEdge);

        var yStart = Math.floor((1 - Math.log(Math.tan(north * Math.PI / 180) + 1 / Math.cos(north * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);
        var yEnd = Math.floor((1 - Math.log(Math.tan(south * Math.PI / 180) + 1 / Math.cos(south * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);

        currentProcessed_count = 0;
        currentToBeProcessed_count = 0;

        // Tiles
        for (var x = xStart; x <= xEnd; x++) {
            for (var y = yStart; y <= yEnd; y++) {

                var tile = {
                    'id': null,
                    'north': null,
                    'south': null,
                    'east': null,
                    'west': null,
                };

                tile.south = tileToLat(y + 1, tilesPerEdge);
                tile.north = tileToLat(y, tilesPerEdge);
                tile.west = tileToLng(x, tilesPerEdge);
                tile.east = tileToLng(x + 1, tilesPerEdge);

                tile.id = zoom + "_" + x + "_" + y + "_" + minLevel + "_8_100";

                if (tilesProcessed.findIndex(testTile, tile) == -1) {

                    currentToBeProcessed_count += 1;

                    tilesToBeProcessed.push(tile);
                }
           }
        }

        scanning = true;

        $('#loading_msg_text').show();
        $('#loading_data_circle').show();

        processTileRequest();
    };

    window.stopScanning = function() {

        scanning = false;

        $('#loading_msg_text').hide();
        $('#loading_data_circle').hide();
    };
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
