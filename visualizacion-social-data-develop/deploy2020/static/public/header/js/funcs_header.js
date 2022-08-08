
function hoverButtonMenu() {
    if ($('#nav').attr('class') == 'navbar navbar-toggleable-md navbar-light') {
        $('#menu').attr('src', '/static/public/header/images/Boton-Menu-Responsive-ON.jpg');
    } else {
        if ($('#nav').attr('class') == 'navbar navbar-toggleable-md bg-light') {
            $('#menu').attr('src', '/static/public/header/images/Boton-Menu-Responsive-ON.jpg');
        } else {
            $('#menu').attr('src', '/static/public/header/images/Boton-Salir-Menu-Responsive-ON.png');
        }
    }
}
function outButtonMenu() {
    if ($('#nav').attr('class') == 'navbar navbar-toggleable-md navbar-light') {
        $('#menu').attr('src', '/static/public/header/images/Boton-Menu-Responsive-OFF.png');
    } else {
        if ($('#nav').attr('class') == 'navbar navbar-toggleable-md bg-light') {
            $('#menu').attr('src', '/static/public/header/images/Boton-Menu-Responsive-OFF.png');
        } else {
            $('#menu').attr('src', '/static/public/header/images/Boton-Salir-Menu-Responsive-OFF.png');
        }
    }
}


function hoverButtonLogin() {
    if ($('#nav').attr('class') == 'navbar navbar-toggleable-md navbar-light') {
        $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-ON.png');
    } else {
        if ($('#nav').attr('class') == 'navbar navbar-toggleable-md bg-light') {
            $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-ON.png');
        } else {
            $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-blanco.png');
        }
    }
}
function outButtonLogin() {
    if ($('#nav').attr('class') == 'navbar navbar-toggleable-md navbar-light') {
        $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-OFF.png');
    } else {
        if ($('#nav').attr('class') == 'navbar navbar-toggleable-md bg-light') {
            $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-OFF.png');
        } else {
            $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-gris.png');
        }
    }
}

function openNav() {
    var height_overlay = $('.overlay').height();
    if (height_overlay == 0) {
        $('.overlay').css('top', $('#header1').height());
        $('#myNav').height($(window).height() - $('#header1').height());
        $('#logo').attr('src', '/static/public/header/images/AOD-Logo-Responsive.png');
        $('#nav').attr('class', 'navbar navbar-toggleable-md bg-inverse');
        $('#nav').css('background-color', 'rgba(0,0,0, 0.82)');
        $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-gris.png');
        $('#menu').attr('src', '/static/public/header/images/Boton-Salir-Menu-Responsive-OFF.png');
    } else {
        $('body,html').css('overflow-y', 'auto');
        $('#myNav').height('0%');
        $('#nav').attr('class', 'navbar navbar-toggleable-md bg-light');
        $('#logo').attr('src', '/static/public/header/images/AOD-Logo.png');
        $('#login').attr('src', '/static/public/header/images/Boton-Acceso-Usuarios-OFF.png');
        $('#menu').attr('src', '/static/public/header/images/Boton-Menu-Responsive-OFF.png');
        $('#buscador_header').val('');
        $('#resultsList').css('visibility', 'hidden');
    }
}

$(document).ready(function () {
    $(window).resize(function () {
        $('.overlay').css('top', $('#header1').height());
        if ($('.overlay').height() != 0) {
            $('#myNav').height($(window).height() - $('#header1').height());
        }
    });
});

function buscaCkan() {
    text = document.getElementById("buscador_header").value;
    window.location.href = "/datos/catalogo?texto=" + text;
    return false;
}

$(document).ready(function () {
    $(window).resize(function () {
        $('.overlay').css('top', $('#header1').height());
        if ($('.overlay').height() != 0) {
            $('#myNav').height($(window).height() - $('#header1').height());
        }
    });
});

function autocompleteRequest() {
    if ($('#buscador_header').val().length >= 3) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var json = JSON.parse(JSON.parse(this.responseText));
                if (json.result.length > 0) {
                    $('#resultsList').css('visibility', 'visible');
                    for (i = 0; i < json.result.length; i++) {
                        document.getElementById('searchResult' + (i + 1)).innerHTML = json['result'][i].title;
                        document.getElementById('searchResult' + (i + 1)).href = '/datos/catalogo/dataset/' + json['result'][i].name;
                    }
                } else {
                    $('#resultsList').css('visibility', 'hidden');
                }
            }
        };
        xhttp.open("GET", "/aod/services/web/datasets/autocomplete?text="
            + $('#buscador_header').val() + "&limit=4", true);
        xhttp.send();
    } else {
        $('#resultsList').css('visibility', 'hidden');
    }
}

$(function () {
    $.get("/static/public/header/header.html", function(data){
        $("#header").html(data);
    });
    $.get("/static/public/footer/footer.html", function(data){
        $("#footer").html(data);
    });
});