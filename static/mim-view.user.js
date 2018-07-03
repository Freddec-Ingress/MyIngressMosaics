// ==UserScript==
// @id             iitc-plugin-myingressmosaics@freddec
// @name           IITC plugin: MIM View
// @category       Info
// @author         Freddec ingress
// @version        0.3
// @description    MIM View. Register missions to MIM site and display mosaics.
// @namespace      https://www.myingressmosaics.com
// @include        https://*.ingress.com/intel*
// @include        http://*.ingress.com/intel*
// @match          https://*.ingress.com/intel*
// @match          http://*.ingress.com/intel*
// @include        https://*.ingress.com/mission/*
// @include        http://*.ingress.com/mission/*
// @match          https://*.ingress.com/mission/*
// @match          http://*.ingress.com/mission/*
// @downloadURL    https://www.myingressmosaics.com/static/mim-view.user.js
// @updateURL      https://www.myingressmosaics.com/static/mim-view.user.js
// @supportURL     https://plus.google.com/communities/104595846633880114608
// @grant          none
// ==/UserScript==

function wrapper(plugin_info) {

    var decodeMissionSummary = function(data) {
        return {
            guid: data[0],
            name: data[1].replace(/\d+/g, ''),
            title: data[1],
            image: data[2],
            ratingE6: data[3],
            mim_status: 'Refreshing...',
            mosaic_ref: null,
            medianCompletionTimeMs: data[4]
        };
    };

	function updateCookie(name, value) {

		var date = new Date();
        date.setTime(date.getTime() + (100 * 24 * 60 * 60 * 1000));

		var delay = date.toGMTString();

		document.cookie = name + '=' + value + '; expires=' + delay + '; path=/';
	}

	function readCookie(name) {

		var C, i, c = document.cookie.split('; ');

		var cookies = {};
		for (i = c.length - 1; i >= 0; i--) {
			C = c[i].split('=');
			cookies[C[0]] = unescape(C[1]);
		}

		return cookies[name];
	}

    // Ensure plugin framework is there
    if (typeof window.plugin !== 'function') {
        window.plugin = function() {};
    }

    // Plugin code
    window.plugin.mim_view = {

        username: null,

        hide_registered_missions: true,
        auto_registration: true,

        missions_map: new Map(),
        displayed_missions_map: new Map(),

        toggleRegisteredMissions: function() {

            window.plugin.mim_view.hide_registered_missions = !window.plugin.mim_view.hide_registered_missions;
            updateCookie('hide_registered_missions', this.hide_registered_missions);

            if (window.plugin.mim_view.hide_registered_missions) document.getElementById('hide-registered-check').checked = true;
            else document.getElementById('hide-registered-check').checked = false;
        },
        
        toggleAutoRegistration: function() {

            window.plugin.mim_view.auto_registration = !window.plugin.mim_view.auto_registration;
            updateCookie('auto_registration', this.auto_registration);

            if (window.plugin.mim_view.auto_registration) document.getElementById('auto-reg-check').checked = true;
            else document.getElementById('auto-reg-check').checked = false;
        },

        // Sending request to MIM site function
        sendMIMRequest: function(request, data, callback=null, errorcallback=null) {

            $.ajax({
                url: 'https://www.myingressmosaics.com/api/' + request,
                type: 'POST',
                data: JSON.stringify(data),
                error: errorcallback,
                success: callback,
                dataType: 'json',
                contentType: 'application/json',
                crossDomain: !0,
            });
        },

        // Install function
        setup: function() {

            this.username = $(".player_nickname").text();

            var value = readCookie('auto_registration');
            if (value === 'false') window.plugin.mim_view.auto_registration = false;

            updateCookie('auto_registration', window.plugin.mim_view.auto_registration);

            var value = readCookie('hide_registered_missions');
            if (value === 'false') window.plugin.mim_view.hide_registered_missions = false;
            
            updateCookie('hide_registered_missions', window.plugin.mim_view.hide_registered_missions);
            
            $('#toolbox').append('<a tabindex="0" onclick="plugin.mim_view.open();">MIM View</a>');

            var css_string = '' +

                '#mim-view { margin:-12px; }' +
                '#mim-view-list { height:300px; overflow-y:scroll; }' +

                '.flex-row { display:flex; flex-direction:row; }' +
                '.flex-col { display:flex; flex-direction:column; }' +

                '.align-center { align-items:center; }' +
                '.align-stretch { align-items:stretch; }' +

                '.justify-center { justify-content:center; }' +

                '.grow { flex-grow:1; }' +

                '.inner { padding:.25rem; }' +

                '.no-padding-bottom { padding-bottom:0!important; }' +

                '.outer { margin:.125rem; }' +

                '.bg-dark { background-color:rgba(0, 0, 0, 0.3); }' +

                '.b-radius { border-radius:.375rem; }' +

                '.text-big { font-size:125%; line-height:125%; }' +
                '.text-small { font-size:90%; line-height:125%; }' +

                '.c-danger { color:#f44336; }' +
                '.c-success { color:#28a745; }' +
                '.c-warning { color:#ffc107; }' +
                '.c-secondary { color:#6c757d; }' +

                '.btn { padding:.125rem .25rem!important; border-radius:.375rem; cursor:pointer; text-align:center; background-color:rgba(8, 48, 78, 0.9); font-size:12px; font-family: "Roboto", "Helvetica Neue", Helvetica, sans-serif; }' +
                '.btn:disabled { color:#6c757d!important; border-color:#6c757d!important; }' +

                '.btn-secondary { border-color:#6c757d!important; color:#bbbbbb!important; }' +
            '';

            $('<style>').prop('type', 'text/css').html(css_string).appendTo('head');

            window.addHook('mapDataRefreshStart', this.refresh.bind(this));
        },

        // Refreshing function
        refresh: function() {

            var bounds = window.map.getBounds();
            window.plugin.mim_view.loadMissions(bounds);
        },

        // Opening function
        open: function() {

            window.plugin.mim_view.showDialog();
            window.plugin.mim_view.refresh();
        },

        // Loading missions function
        loadMissions: function(bounds) {

            var block_refresh = $('#mim-view-refresh');
            block_refresh.show('display');

            var block_list = $('#mim-view-list');
            block_list.empty();

            window.postAjax('getTopMissionsInBounds', {

                westE6: ((bounds.getWest() * 1000000) | 0),
                eastE6: ((bounds.getEast() * 1000000) | 0),
                northE6: ((bounds.getNorth() * 1000000) | 0),
                southE6: ((bounds.getSouth() * 1000000) | 0),

            }, function(data) {

                var missions = data.result.map(decodeMissionSummary);
                if (!missions) {

                    if (errorcallback) errorcallback('Invalid data');
                    return;
                }

                var mim_data = [];

                window.plugin.mim_view.displayed_missions_map = [];

                missions.forEach(function(mission) {

                    var m_data = window.plugin.mim_view.missions_map.get(mission.guid);
                    if (!m_data) {
                        window.plugin.mim_view.missions_map.set(mission.guid, mission);
                        m_data = window.plugin.mim_view.missions_map.get(mission.guid);
                    }

                    window.plugin.mim_view.displayed_missions_map.push(m_data);

                    var temp = { mid: mission.guid };
                    mim_data.push(temp);
                });

                window.plugin.mim_view.sendMIMRequest('ext_check/', mim_data, function(response) {

                    block_refresh.hide();

                    var temp = [];

                    response.data.forEach(function(mission) {

                        var m_data = window.plugin.mim_view.missions_map.get(mission.mid);
                        if (m_data) {

                            switch (mission.status) {

                                case 'notregistered':
                                    m_data.mosaic_ref = null;
                                    m_data.mim_status = 'Not Registered';
                                    break;

                                case 'completed':
                                    m_data.mosaic_ref = mission.mosaicref;
                                    m_data.mim_status = 'In Mosaic';
                                    break;

                                case 'incomplete':
                                    m_data.mosaic_ref = mission.mosaicref;
                                    m_data.mim_status = 'In Incomplete';
                                    break;

                                case 'registered':
                                    m_data.mosaic_ref = null;
                                    m_data.mim_status = 'Registered';
                                    break;
                            }

                            temp.push(m_data);
                        }
                    });

                    temp.sort(function(a, b) {
                        if (a.name > b.name) return 1;
                        if (a.name < b.name) return -1;
                        return 0;
                    });

                    block_list.empty();

                    var obj_block_list = document.getElementById('mim-view-list');
                    temp.forEach(function(mission) {
                        obj_block_list.appendChild(window.plugin.mim_view.renderMission(mission));
                    });

                    if (window.plugin.mim_view.auto_registration) window.plugin.mim_view.registerAllMissions();
                });

            });
        },

        // Showing dialog function
        showDialog: function() {

            dialog({
                html: this.renderDialog(),
                title: 'MIM View',
                width: '300px',
                height: 'auto',
                buttons: null,
            });
        },

        // Rendering dialog function
        renderDialog: function() {

            var container = document.createElement('div');
            container.id = 'mim-view';

            var block1 = container.appendChild(document.createElement('div'));
            block1.className = 'flex-row align-center inner';

            var item_auto_register = block1.appendChild(document.createElement('div'));
            item_auto_register.className = 'flex-col grow';

            var line1 = item_auto_register.appendChild(document.createElement('div'));
            line1.className = 'flex-row align-center inner';
            
            var m_check = line1.appendChild(document.createElement('input'));
            m_check.id = 'auto-reg-check';
            m_check.type = 'checkbox';
            m_check.addEventListener('click', function() {window.plugin.mim_view.toggleAutoRegistration();});

            if (window.plugin.mim_view.auto_registration) m_check.checked = true;
            else m_check.checked = false;

            var m_label = line1.appendChild(document.createElement('a'));
            m_label.textContent = 'Auto-registration';
            m_label.addEventListener('click', function() {window.plugin.mim_view.toggleAutoRegistration();});

            var line2 = item_auto_register.appendChild(document.createElement('div'));
            line1.className = 'flex-row align-center inner';
            
            var m_check = line2.appendChild(document.createElement('input'));
            m_check.id = 'hide-registered-check';
            m_check.type = 'checkbox';
            m_check.addEventListener('click', function() {window.plugin.mim_view.toggleRegisteredMissions();});

            if (window.plugin.mim_view.hide_registered_missions) m_check.checked = true;
            else m_check.checked = false;

            var m_label = line1.appendChild(document.createElement('a'));
            m_label.textContent = 'Hide registered';
            m_label.addEventListener('click', function() {window.plugin.mim_view.toggleRegisteredMissions();});
            
            var item_register_all = block1.appendChild(document.createElement('div'));
            item_register_all.className = 'inner';

            var m_button = item_register_all.appendChild(document.createElement('button'));
            m_button.id = 'mim_autoreg_btn';
            m_button.textContent = 'Register all';
            m_button.className = 'btn';
            m_button.addEventListener('click', function() {window.plugin.mim_view.registerAllMissions();});

            var block2 = container.appendChild(document.createElement('div'));
            block2.id = 'mim-view-refresh';
            block2.className = 'flex-row justify-center';

            var refresh_label = block2.appendChild(document.createElement('span'));
            refresh_label.className = 'c-warning';
            refresh_label.textContent = 'Refreshing...';

            var block3 = container.appendChild(document.createElement('div'));
            block3.id = 'mim-view-list';

            return container;
        },

        // Rendering mission function
        renderMission: function(mission) {

            if (window.hide_registered_missions && mission.mim_status == 'Registered' ) {
                return null;
            }
            
            var container = document.createElement('div');
            container.className = 'flex-row inner outer bg-dark b-radius';

            var block1 = container.appendChild(document.createElement('div'));
            block1.className = 'flex-row inner';

            var m_img = block1.appendChild(document.createElement('img'));
            m_img.src = mission.image;
            m_img.width = 35;
            m_img.height = 35;

            var block2 = container.appendChild(document.createElement('div'));
            block2.className = 'flex-col inner grow';

            var line1 = block2.appendChild(document.createElement('div'));
            line1.className = 'flex-row';

            var m_title = line1.appendChild(document.createElement('span'));
            m_title.textContent = mission.title;

            var line2 = block2.appendChild(document.createElement('div'));
            line2.className = 'flex-row align-center';
            line2.style.margin = '5px 0 0 0';

            var m_status = line2.appendChild(document.createElement('span'));
            m_status.id = 'mim_status_' + mission.guid;
            m_status.className = 'grow text-small';
            m_status.textContent = mission.mim_status;

            switch (mission.mim_status) {

                case 'Registered': m_status.className += ' c-secondary'; break;
                case 'Not Registered': m_status.className += ' c-danger'; break;
                case 'In Mosaic': m_status.className += ' c-success'; break;
                case 'In Incomplete': m_status.className += ' c-warning'; break;
            }

            switch (mission.mim_status) {

                case 'Registered':
                    var m_button = line2.appendChild(document.createElement('button'));
                    m_button.id = 'mim_btn_' + mission.guid;
                    m_button.textContent += 'Update';
                    m_button.style.width = '65px';
                    m_button.className = 'btn btn-secondary';
                    m_button.addEventListener('click', function() {window.plugin.mim_view.updateMission(mission);});
                    break;

                case 'Not Registered':
                    var m_button = line2.appendChild(document.createElement('button'));
                    m_button.id = 'mim_btn_' + mission.guid;
                    m_button.textContent += 'Register';
                    m_button.style.width = '65px';
                    m_button.className = 'btn';
                    m_button.addEventListener('click', function() {window.plugin.mim_view.registerMission(mission);});
                    break;

                case 'In Mosaic':
                    var m_link = line2.appendChild(document.createElement('a'));
                    m_link.textContent += 'MIM Link';
                    m_link.className = 'btn';
                    m_link.style.width = '57px';
                    m_link.href = 'https://www.myingressmosaics.com/mosaic/' + mission.mosaic_ref;
                    m_link.target = '_blank';
                    break;

                case 'In Incomplete':
                    var m_link = line2.appendChild(document.createElement('a'));
                    m_link.textContent += 'MIM Link';
                    m_link.className = 'btn';
                    m_link.style.width = '57px';
                    m_link.href = 'https://www.myingressmosaics.com/waiting/' + mission.mosaic_ref;
                    m_link.target = '_blank';
                    break;
            }

            return container;
        },

        updateMission: function(mission) {

            var m_status = document.getElementById('mim_status_' + mission.guid);
            m_status.textContent = 'Refreshing...';
            m_status.className = 'grow text-small c-warning';

            var m_button = document.getElementById('mim_btn_' + mission.guid);
            m_button.disabled = true;

            var data = { guid:mission.guid };
            window.postAjax('getMissionDetails', data, function(response) {

                response.result.push(this.username);

                window.plugin.mim_view.sendMIMRequest('ext_register/', response.result, function(response) {

                    m_status.textContent = 'Updated';
                    m_status.className = 'grow text-small c-secondary';

                    m_button.disabled = false;
                });
            });
        },

        registerMission: function(mission) {

            var m_status = document.getElementById('mim_status_' + mission.guid);
            m_status.textContent = 'Refreshing...';
            m_status.className = 'grow text-small c-warning';

            var m_button = document.getElementById('mim_btn_' + mission.guid);
            m_button.disabled = true;

            var data = { guid:mission.guid };
            window.postAjax('getMissionDetails', data, function(response) {

                response.result.push(this.username);

                window.plugin.mim_view.sendMIMRequest('ext_register/', response.result, function(response) {

                    m_status.textContent = 'Registered';
                    m_status.className = 'grow text-small c-secondary';

                    m_button.disabled = false;
                    m_button.textContent = 'Update';
                    m_button.className = 'btn btn-secondary';
                    m_button.addEventListener('click', function() {window.plugin.mim_view.updateMission(mission);});
                });
            });
        },

        registerAllMissions: function() {

            var m_button = document.getElementById('mim_autoreg_btn');
            if (m_button) m_button.disabled = true;

            window.plugin.mim_view.displayed_missions_map.forEach(function(mission) {

                if (mission.mim_status == 'Not Registered') {
                    window.plugin.mim_view.registerMission(mission);
                }
            });

            if (m_button) m_button.disabled = false;
        }
    };

    // Install plugin
    var setup = window.plugin.mim_view.setup.bind(window.plugin.mim_view);
    setup.info = plugin_info;
    if (!window.bootPlugins) window.bootPlugins = [];
    window.bootPlugins.push(setup);

    // If IITC has already booted, immediately install plugin
    if (window.iitcLoaded && typeof setup === 'function') setup();
}

// Inject plugin code into site

var script = document.createElement('script');

var info = {};

if (typeof GM_info !== 'undefined' && GM_info && GM_info.script) {

    info.script = {
        name: GM_info.script.name,
        version: GM_info.script.version,
        description: GM_info.script.description
    };
}

script.appendChild(document.createTextNode('(' + wrapper + ')(' + JSON.stringify(info) + ');'));
(document.body || document.head || document.documentElement).appendChild(script);