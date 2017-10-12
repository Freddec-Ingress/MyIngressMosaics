// ==UserScript==
// @id             myingressmosaics@freddec
// @name           MyIngressMosaics Scanning plugin
// @version        1.0.11
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
    '#tm_zoom {margin-top:10px; font-size:13px;}' +
    '#loading_data_circle {display:none; animation: rotating 2s linear infinite;}' +
    '#loading_msg_text {display:none;}' +
    '#loading_msg {display:block!important;}' +
    '#dashboard_container {top:50px!important;}' +
    '#tm_start {padding: 0 5px; position: absolute; bottom: -45px; right: 0px;}' +
    '#tm_stop {padding: 0 5px; position: absolute; bottom: -45px; right: 0px; display:none;}' +
    '#tm_view_container {display:none!important;}' +
    '#tm_header {display:none!important; width:310px;}' +
    '#tm_main {display:none!important; width:310px; height:calc(100% - 37px);}' +
    '.tm_list_element + .tm_list_element {border-top: 0; padding:5px 10px;}' +
    '.tm_mission_title {font-size:13px; width: 275px;}' +
    '.bottom_right_tab_button {width:160px;}' +
'</style>';

//--------------------------------------------------------------------------------------------------
// HTML updates

document.getElementById('dashboard_container').innerHTML +=
    '<div id="tm_zoom"></div>' +
    '<div id="tm_start" class="unselectable bottom_right_tab_button" onclick="expertScanning();">' +
    '       Start scanning' +
    '</div>';

document.getElementById('dashboard_container').innerHTML +=
    '<div id="tm_stop" class="unselectable bottom_right_tab_button" onclick="stopScanning();">' +
    '       Stop scanning' +
    '</div>';

document.getElementById('dashboard_container').innerHTML +=
    '<div id="tm_check" class="unselectable bottom_right_tab_button" onclick="checkBounds();">' +
    '       Check missions' +
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

        if (successCallback) {
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

function callMIMAPI(action, data, successCallback, errorCallback) {

    var post_data = data;

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

    var result = $.ajax("https://www.myingressmosaics.com/api/" + action + "/", {
        type: 'POST',
        data: JSON.stringify(post_data),
        dataType: 'json',
        success: [onSuccess],
        error: [onError],
        contentType: 'application/json; charset=utf-8',
    });

    result.action = action;

    return result;
}

//--------------------------------------------------------------------------------------------------
// Functions to process location

var currentLocation = '';
var locationsToBeProcessed = [];

var geocoder = new google.maps.Geocoder();

function processNextLocation() {

    if (locationsToBeProcessed.length < 1) {
        return;
    }

    var location = locationsToBeProcessed.slice(0, 1);

    currentLocation = String(location);
    console.log('Location: ' + currentLocation);

    geocoder.geocode({'address': currentLocation}, function(results, status) {

        if (status === 'OK') {

            M.setCenter(results[0].geometry.location);
            M.setZoom(14);

            window.startScanning();
        }

        locationsToBeProcessed.splice(0, 1);
    });
}

//--------------------------------------------------------------------------------------------------
// Functions to process tile request and tile data

var tilesProcessed = [];
var tilesToBeProcessed = [];

var currentProcessed_count = 0;
var currentToBeProcessed_count = 0;

var portalsToBeProcessed = [];

var missionsProcessed = [];
var missionsInProcess = [];
var missionsToBeProcessed = [];

function processNextTiles() {

    if (!scanning || tilesToBeProcessed.length < 1) {

        tilesToBeProcessed = [];

        currentProcessed_count = 0;
        currentToBeProcessed_count = 0;

        portalsToBeProcessed = [];

        missionsProcessed = [];
        missionsInProcess = [];
        missionsToBeProcessed = [];

        currentProcessed_count = 0;
        currentToBeProcessed_count = 0;

        processNextLocation();

        scanning = false;

        $('#tm_start').show();
        $('#tm_stop').hide();

        $('#loading_msg_text').hide();
        $('#loading_data_circle').hide();

        return;
    }

    var data = { tileKeys: [] };

    var tiles = tilesToBeProcessed.slice(0, 12);
    for (var tile of tiles) {

        data.tileKeys.push(tile.id);

        tile.rect.setOptions({
            strokeColor: '#550000',
            fillColor: '#550000',
        });
    }

    callIngressAPI('getEntities', data, function(data, textStatus, jqXHR) {

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

                if (tilesProcessed.indexOf(tile) != -1) {

                    tilesToBeProcessed.splice(tilesToBeProcessed.indexOf(tile), 1);
                    continue;
                }

                tilesProcessed.push(tile);
                tilesToBeProcessed.splice(tilesToBeProcessed.indexOf(tile), 1);

                tile.rect.setOptions({
                    strokeColor: '#555500',
                    fillColor: '#555500',
                });

                currentProcessed_count += 1;
                var text = '' + currentProcessed_count + '/' + currentToBeProcessed_count;
                document.getElementById('loading_msg_text').innerHTML = 'Scanning Data... ' + text;

                var has_portal = false;

                for (var item of val.gameEntities) {
                    if (item[2][0] == 'p' && item[2][10] === true) {

                        var portal = {
                            'id': item[0],
                            'lat': item[2][2] / 1000000.0,
                            'lng': item[2][3] / 1000000.0,
                        };

                        portalsToBeProcessed.push(portal);

                        has_portal = true;
                    }
                }

                if (has_portal) {

                    var dataBounds = {
                        eastE6: Math.trunc(tile.east * 1000000),
                        northE6: Math.trunc(tile.north * 1000000),
                        southE6: Math.trunc(tile.south * 1000000),
                        westE6: Math.trunc(tile.west * 1000000),
                    };

                    callIngressAPI('getTopMissionsInBounds', dataBounds, function(data, textStatus, jqXHR) {

                        if (!data.result) return;

                        for (var item of data.result) {

                            var mission_id = item[0];
                            missionsToBeProcessed.push(mission_id);
                        }

                    }, function(jqXHR, textStatus, errorThrown) {
                    });
                }
            }
        }

        processNextPortal();

    }, function(jqXHR, textStatus, errorThrown) {

        setTimeout(processNextTiles, 1000);
    });
}

//--------------------------------------------------------------------------------------------------
// Functions to process portal request and portal data

function processNextPortal() {

    if (portalsToBeProcessed.length < 1) {

        processNextTiles();
        return;
    }

    var portal = portalsToBeProcessed[0];

    var data = { guid: portal.id };
    callIngressAPI('getTopMissionsForPortal', data, function(data, textStatus, jqXHR) {

        if (data && data.result) {
            for (var item of data.result) {

                var mission_id = item[0];
                missionsToBeProcessed.push(mission_id);
            }
        }

        portalsToBeProcessed.splice(0, 1);

        processNextMission();

    }, function(jqXHR, textStatus, errorThrown) {

        setTimeout(processNextPortal, 1000);
    });
}

//--------------------------------------------------------------------------------------------------
// Functions to process mission request and mission data

var mImageEnl = {
    url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/enl_lev8.png',
    scaledSize: new google.maps.Size(25, 25),
    origin: new google.maps.Point(0, 0),
    anchor: new google.maps.Point(12, 13),
};

function processNextMission() {

    if (missionsToBeProcessed.length < 1) {
        processNextPortal();
        return;
    }

    var mission_id = missionsToBeProcessed[0];

    if (missionsInProcess.indexOf(mission_id) != -1) {

        missionsToBeProcessed.splice(0, 1);
        processNextMission();
        return;
    }

    missionsInProcess.push(mission_id);

    var data = { guid: mission_id };
    callIngressAPI('getMissionDetails', data, function(data, textStatus, jqXHR) {

        if (!data.result) return;

        if (missionsProcessed.indexOf(mission_id) != -1) {

            missionsToBeProcessed.splice(0, 1);
            processNextMission();
            return;
        }

        missionsProcessed.push(mission_id);
        missionsToBeProcessed.splice(0, 1);

        data.result.push(username);
        var requestData = data.result;
        callMIMAPI('ext_register', data.result, function(data, textStatus, jqXHR) {

            if (requestData[9][0][5] && data == 'Registered') {

                console.log('\t' + requestData[1]);

                var marker = new google.maps.Marker({
                    position: {lat: requestData[9][0][5][2]/1000000.0, lng: requestData[9][0][5][3]/1000000.0},
                    map: M,
                    icon: mImageEnl,
                });
            }
            if (requestData[9][0][5] && data == 'Updated') {

                var marker = new google.maps.Marker({
                    position: {lat: requestData[9][0][5][2]/1000000.0, lng: requestData[9][0][5][3]/1000000.0},
                    map: M,
                    icon: mImageRes,
                });
            }
        });

        processNextMission();

    }, function(jqXHR, textStatus, errorThrown) {

        setTimeout(processNextMission, 1000);
    });
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

function findTileFunc(element, index, array) {

    if (this.id == element.id) {return true;}
    return false;
}

var mImageRes = {
    url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/hum_lev8.png',
    scaledSize: new google.maps.Size(25, 25),
    origin: new google.maps.Point(0, 0),
    anchor: new google.maps.Point(12, 13),
};

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

    window.Map = M;

    document.getElementById('tm_zoom').innerHTML = 'Zoom: ' + MAP_PARAMS.zoom;

    M.addListener('zoom_changed', function(event) {

        document.getElementById('tm_zoom').innerHTML = 'Zoom: ' + M.getZoom();
    });

    // Scanning functions
    window.startScanning = function() {

        if (scanning === true) return;

        window.checkBounds();

        tilesToBeProcessed = [];

        var bds = M.getBounds();

        var west = bds.getSouthWest().lng();
        var east = bds.getNorthEast().lng();
        var north = bds.getNorthEast().lat();
        var south = bds.getSouthWest().lat();

        var zoom = 19;
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
                    'rect': null,
                };

                tile.id = zoom + "_" + x + "_" + y + "_" + minLevel + "_8_100";

                if (tilesProcessed.findIndex(findTileFunc, tile) == -1 && tilesToBeProcessed.indexOf(findTileFunc, tile) == -1) {

                    tile.south = tileToLat(y + 1, tilesPerEdge);
                    tile.north = tileToLat(y, tilesPerEdge);
                    tile.west = tileToLng(x, tilesPerEdge);
                    tile.east = tileToLng(x + 1, tilesPerEdge);

                    tile.rect = new google.maps.Rectangle({
                        strokeColor: '#555555',
                        strokeOpacity: 0.5,
                        strokeWeight: 1,
                        fillColor: '#555555',
                        fillOpacity: 0.25,
                        map: M,
                        bounds: {
                            north: tile.north,
                            south: tile.south,
                            east: tile.east,
                            west: tile.west
                        }
                    });

                    currentToBeProcessed_count += 1;

                    tilesToBeProcessed.push(tile);
                }
           }
        }

        scanning = true;

        $('#tm_start').hide();
        $('#tm_stop').show();

        $('#loading_msg_text').show();
        $('#loading_data_circle').show();

        processNextTiles();
    };

    window.stopScanning = function() {

        for (var tile of tilesToBeProcessed) {
            tile.rect.setMap(null);
        }

        tilesToBeProcessed = [];

        currentProcessed_count = 0;
        currentToBeProcessed_count = 0;

        portalsToBeProcessed = [];

        missionsProcessed = [];
        missionsInProcess = [];
        missionsToBeProcessed = [];

        scanning = false;

        $('#tm_start').show();
        $('#tm_stop').hide();

        $('#loading_msg_text').hide();
        $('#loading_data_circle').hide();
    };

    window.expertScanning = function() {

        if (locationsToBeProcessed.length > 0) {
            processNextLocation();
            return;
        }

        window.startScanning();
    };

    window.checkBounds = function() {

        var center = M.getCenter();

        var bds = M.getBounds();

        var South_Lat = bds.getSouthWest().lat();
        var South_Lng = bds.getSouthWest().lng();
        var North_Lat = bds.getNorthEast().lat();
        var North_Lng = bds.getNorthEast().lng();

        var data = { sLat: South_Lat, sLng: South_Lng, nLat: North_Lat, nLng: North_Lng };
        callMIMAPI('ext_bounds', data, function(data, textStatus, jqXHR) {

            if (data) {

                for (var item of data) {

                    if (missionsProcessed.indexOf(item.ref) == -1) {

                        missionsProcessed.push(item.ref);

                        var latLng = new google.maps.LatLng(item.startLat, item.startLng);
                        var marker = new google.maps.Marker({
                            position: latLng,
                            map: M,
                            icon: mImageRes,
                        });
                    }
                }
            }
        });
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
