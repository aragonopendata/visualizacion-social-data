angular.module('aosd.controllers', [])

  // .controller('generalController', function ($scope, $location, settings, escuchaAPI, selection, helpers) {
  // })
  .controller('searchController', function ($scope, settings, escuchaAPI, selection, drawers, helpers) {
    $scope.region = (selection.region == '*') ? 'Todo Aragón' : selection.region;
    $scope.start = (selection.start == '') ? '1/12/2013' : selection.start;
    $scope.end = (selection.end == '') ? helpers.dateToStr(new Date()) : selection.end;
    $scope.terms = selection.terms;
  })
  .controller('searchChartController', function ($scope, settings, escuchaAPI, selection, drawers, helpers) {
    $scope.drawTotals = function () {
      if (selection.totals === null) {
        escuchaAPI.getTotals(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
          selection.totals = response;
          drawers.drawTotals($scope, selection.totals);
        });
      } else {
        drawers.drawTotals($scope, selection.totals);
      }

    }

    $scope.drawTotals();
  })
  
  /* Main controller */
  .controller('mainController', function ($scope, $location, settings, escuchaAPI, selection, helpers) {
    $scope.region = selection.region;
    $scope.regions = [{'id': '*', 'label': 'TODO ARAGÓN'}];
    $scope.start = selection.start;
    $scope.end = selection.end;

    $scope.choices = [];

    for (i=0; i<selection.terms.length; i++) {
      $scope.choices.push({'id': i+1, 'name': selection.terms[i]});
    }
    if(!selection.terms.length) $scope.choices.push({'id':1, 'name':'*'})
    // Reset the last search
    selection.totals = null;

    $scope.invalid_dates = '';
    $scope.termsList = sessionStorage.getItem('terms') ? sessionStorage.getItem('terms') : $scope.choices[0].name;
    sessionStorage.removeItem('terms')

    $('.input-daterange[readonly!="True"]').datepicker(helpers.dateinputOptions);

    escuchaAPI.getMetadata().success(function (response) {
       $scope.regions.push({'id':'PROV HUESCA' , 'label': 'Huesca' , 'tipo':'provincia'});
       $scope.regions.push({'id':'PROV TERUEL' , 'label': 'Teruel' , 'tipo':'provincia'});
       $scope.regions.push({'id':'PROV ZARAGOZA' , 'label': 'Zaragoza' , 'tipo':'provincia'});
       for (i=0; i<response.regions.length; i++) {
       $scope.regions.push({'id': response.regions[i], 'label': response.regions[i], 'tipo':'comarca'});
       }
       for (i=0; i<response.mun.length; i++) {
         $scope.regions.push({'id': 'MUN '+response.mun[i], 'label':response.mun[i],'tipo':'municipio'});
       }
    });

    $scope.validate_dates = function() {
      if ($scope.start == '' || $scope.end == '') {
        return true;
      } else {
        dstart = helpers.strToDate($scope.start);
        dend = helpers.strToDate($scope.end);
        return dstart <= dend;
      }
    }

    //deberiamos usar la misma search pero simplemente consultar el boton que ha pulsado
    $scope.search_inst = function() {

      // Validate
      if (! $scope.validate_dates() ) {
        $scope.invalid_dates = 'La fecha de inicio no puede ser mayor que la de fin.';
        return;
      }
      
      $scope.choices = $scope.termsList ? $scope.termsList.split(" ") : "";

      selection.region = $scope.region;
      selection.start = $scope.start;
      selection.end = $scope.end;
      selection.terms = [];
      for (i=0; i<$scope.choices.length; i++) {
        var q = $scope.choices[i] ? $scope.choices[i] : '*';
        if (selection.terms.indexOf(q) == -1) {
          selection.terms.push(q);
        }
      }

      var termsFormated = "";
      for (i=0; i<selection.terms.length; i++) {
        if (i == selection.terms.length - 1){
          termsFormated += selection.terms[i];
        }else{
        termsFormated += selection.terms[i] + ' ';
        }
      }

      sessionStorage.setItem('terms', termsFormated);
      
      // $location.path('/stats_inst').search({    // Default url for every search
      $location.path($location.path()).search({
        'region': selection.region,
        'start': selection.start,
        'end': selection.end,
        'term': selection.terms,
        'enlista': true,
      });
    }

    // $scope.search = function() {
    //   // Validate
    //   if (! $scope.validate_dates() ) {
    //     $scope.invalid_dates = 'La fecha de inicio no puede ser mayor que la de fin.';
    //     return;
    //   }

    //   $scope.choices = $scope.termsList ? $scope.termsList.split(" ") : "";

    //   selection.region = $scope.region;
    //   selection.start = $scope.start;
    //   selection.end = $scope.end;
    //   selection.terms = [];
    //   for (i=0; i<$scope.choices.length; i++) {
    //     var q = $scope.choices[i] ? $scope.choices[i] : '*';
    //     if (selection.terms.indexOf(q) == -1) {
    //       selection.terms.push(q);
    //     }
    //   }

    //   $location.path('/stats').search({
    //     'region': selection.region,
    //     'start': selection.start,
    //     'end': selection.end,
    //     'term': selection.terms,
    //   });
    // }
  })

  /* SideNav controller */
  // .controller('sidenavController', function ($scope, $location, selection) {
  //   $scope.isActive = function (path) {
  //     var currentPath = $location.path().split('/')[1];
  //     if (currentPath.indexOf('?') !== -1) {
  //       currentPath = currentPath.split('?')[0];
  //     }
  //     return currentPath === path.split('/')[1];
  //   }

  //   $scope.moveTo = function (path) {
  //     $location.path(path).search({
  //       'region': selection.region,
  //       'start': selection.start,
  //       'end': selection.end,
  //       'term': selection.terms,
  //     });
  //   }
  // })

  /* SideNav Inst controller */
  .controller('sidenavInstController', function ($scope, $location, selection) {
    $scope.isActive = function (path) {
      var currentPath = $location.path().split('/')[1];
      if (currentPath.indexOf('?') !== -1) {
        currentPath = currentPath.split('?')[0];
      }
      return currentPath === path.split('/')[1];
    }

    $scope.moveTo = function (path) {
      $location.path(path).search({
        'region': selection.region,
        'start': selection.start,
        'end': selection.end,
        'term': selection.terms,
        'enlista': selection.enlista,
      });
    }

    $scope.scrollTo = function(id) {
      $location.hash(id);
      // $anchorScroll();
    }
  })



  /* Selection Help controller */
  // .controller('selectionHelpController', function ($scope, settings, escuchaAPI, selection, drawers, helpers) {
  //   $scope.region = (selection.region == '*') ? 'Todo Aragón' : selection.region;
  //   $scope.start = (selection.start == '') ? '1/12/2013' : selection.start;
  //   $scope.end = (selection.end == '') ? helpers.dateToStr(new Date()) : selection.end;
  //   $scope.terms = selection.terms;
  //   $scope.downloadCSV = function () {
  //     BootstrapDialog.confirm({
  //       title: 'Descargar CSV',
  //       message: 'Se descargarán los últimos mensajes que coinciden con su selección hasta un máximo de 20.000 mensajes.\n\n<b>Nota:</b> la generación del CSV puede tardar unos segundos.',
  //       type: BootstrapDialog.TYPE_INFO,
  //       btnCancelLabel: 'Cancelar',
  //       btnOKLabel: 'Aceptar',
  //       callback: function (result) {
  //         if (result) {
  //           encodedParams = $.param({
  //             'terms': selection.apiterms,
  //             'region': selection.region,
  //             'start': selection.start,
  //             'end': selection.end
  //           }).replace(/%5B%5D/g, ''); // JQuery put key[]=value if a param is an array. '%5B%5D' == '[]'
  //           document.location = settings.API_URL + '/get_csv/?' + encodedParams;
  //         }
  //       }
  //     });
  //   }

  //   $scope.drawTotals = function () {
  //     if (selection.totals === null) {
  //       escuchaAPI.getTotals(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
  //         selection.totals = response;
  //         drawers.drawTotals($scope, selection.totals);
  //       });
  //     } else {
  //       drawers.drawTotals($scope, selection.totals);
  //     }

  //   }

  //   $scope.drawTotals();
  // })

  /* Evolution controller */
  .controller('evolutionController', function ($scope, $location, escuchaAPI, selection, drawers, helpers) {
    selection.updateFromQueryString($location.search());

    // $scope.drawEvolution = function () {
    //   escuchaAPI.getMultitermEvolution(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
    //     drawers.drawMultitermEvolution($scope, response);
    //   });
    // }

    $scope.drawEvolutionTotal = function () {
      escuchaAPI.getEvolution(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
        drawers.drawEvolutionTotal($scope, response);
      });
    }

    // $scope.drawEvolution();
    $scope.drawEvolutionTotal();
  })

  /* Heatmap controller */
  .controller('heatmapController', function ($scope, $location, escuchaAPI, selection, drawers, helpers) {
    selection.updateFromQueryString($location.search());

    var raster = new ol.layer.Tile({
      source: new ol.source.OSM()
    })

    var map = new ol.Map({
      layers: [raster],
      target: 'map',
      view: new ol.View({
        center: ol.proj.transform([-0.8833333, 41.6333333], 'EPSG:4326', 'EPSG:3857'),
        zoom: 5
      })
    });

    var ALL_TERMS = 'Todos los de la lista'

    $scope.change_terms = [ALL_TERMS]
    $scope.change_terms = $scope.change_terms.concat(selection.terms);
    $scope.change_terms_selected = ALL_TERMS

    $scope.partial_terms = selection.terms;

    /*$scope.map = {
      center: {latitude: 41.6333333, longitude: -0.8833333},
      zoom: 7,
      showHeat: true
    };*/

    $scope.map = map;
    $scope.heatLayer = null;

    //$scope.map.heatLayer = null;
    $scope.markers = [];
    $scope.markers_items = {};
    $scope.markers_active = false;

    $scope.map_weight = false;

    $scope.weight_min = 0;
    $scope.weight_max = 0;
    $scope.num_items = 0;

    $scope.changeSelection = function () {
      if ($scope.change_terms_selected == ALL_TERMS) {
        $scope.partial_terms = selection.terms;
      } else {
        $scope.partial_terms = $scope.change_terms_selected;
      }
      $scope.drawMap()
    }

    $scope.showLastItems = function () {
      if ($scope.markers_active) {
        $scope.markers = [];
        $scope.markers_items = {};
      } else {
        escuchaAPI.getLastItems($scope.partial_terms, selection.region, selection.start, selection.end, 0, true).success(function (response) {
          $scope.markers = [];
          $scope.markers_items = {};
          for (i = 0; i < response.last_items.length; i++) {
            var item = response.last_items[i];
            var marker = {
              id: item.id,
              coords: {
                latitude: item.geo.lat,
                longitude: item.geo.lon,
              },
              options: {
                icon: '/static/public/socialdata/img/msg-icon.png'
              }
            }
            $scope.markers.push(marker);
            $scope.markers_items[item.id] = {
              id: item.id,
              title: item.title,
              description: item.description,
              author: item.author,
              source: item.source,
              published_on: item.published_on,
            }
          }
        });
      }
      $scope.markers_active = !$scope.markers_active;
    }

    $scope.showMessage = function (item_id) {
      var item = $scope.markers_items[item_id];
      BootstrapDialog.alert({
        title: 'Mensaje del usuario <b>' + item.author + '</b> en <b>' + helpers.titleCase(item.source) + '</b>',
        message: ((item.title === null) ? '' : item.title + '\n\n') + item.description + '\n\n<small><i>' + item.published_on + '</i></small>'
      });
    }

    $scope.map.heatLayerCallback = function (heatLayer) {
      heatLayer.setOptions(helpers.heatmapOptions);
      $scope.map.heatLayer = heatLayer;
      $scope.drawMap();
    }

    $scope.drawMap = function () {
      escuchaAPI.getGeogrid($scope.partial_terms, selection.region, selection.start, selection.end, $scope.map_weight).success(function (response) {
        drawers.drawMap($scope, response);
      });
    }
    // CALL FOR THE FIRST TIME
    $scope.drawMap();

    $scope.changeHeatmapWeight = function () {
      $scope.drawMap();
    }
  })

  /* Stats controller */
  .controller('statsController', function ($scope, $location, escuchaAPI, selection, drawers, helpers) {
    selection.updateFromQueryString($location.search());

    if(_.isEmpty($location.search())) {
      $location.path('/general_inst').search({
        'region': "*",
        'start': "",
        'end': "",
        'term': "*",
        'enlista': true,
      });
      return
    }
    $scope.top_hashtags = [];
    $scope.top_authors = [];
    $scope.top_mentions = [];

    $scope.last_items = [];
    $scope.last_items_page = 0;

    $scope.hemicycle_hashtags = { 'title': { 'text': '' } };
    $scope.hemicycle_mentions = { 'title': { 'text': '' } };

    $scope.moreItems = function () {
      $scope.last_items_page = $scope.last_items_page + 1;
      escuchaAPI.getLastItems(selection.apiterms, selection.region, selection.start, selection.end, $scope.last_items_page).success(function (response) {
        $scope.last_items = $scope.last_items.concat(response.last_items);
      });
    }

    $scope.drawTops = function () {
      escuchaAPI.getTops(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
        drawers.drawHemicycles($scope, response);
        $scope.top_hashtags = response.top_hashtags;
        $scope.top_authors = response.top_authors;
        $scope.top_mentions = response.top_mentions;
      });
    }

    $scope.drawLastItems = function () {
      escuchaAPI.getLastItems(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
        $scope.last_items = response.last_items;
      });
    }

    $scope.drawTops();
    $scope.drawLastItems();
  })

  /* Polarity controller */
  .controller('polarityController', function ($scope, $location, escuchaAPI, selection, drawers, helpers) {
    selection.updateFromQueryString($location.search());

    $scope.polarity_pos = [{ 'Nivel': 0 }];
    $scope.polarity_pos_cols = [{ 'id': 'Nivel', 'type': 'gauge' }];

    $scope.polarity_neg = [{ 'Nivel': -1 }];
    $scope.polarity_neg_cols = [{ 'id': 'Nivel', 'type': 'gauge' }];

    $scope.terms_polarity = [];

    $scope.polarityColor = function (color, d) {
      if (d.value) {
        if (d.value == 0)
          return '#F97600';
        else
          return d.value < 0 ? '#A52A2A' : '#4682B4';
      } else {
        return null;
      }
    }

    $scope.polarityTooltip = function (d) {
      return "Nivel de polaridad";
    }

    $scope.drawPolarity = function () {
      escuchaAPI.getPolarity(selection.apiterms, selection.region, selection.start, selection.end).success(function (response) {
        drawers.drawPolarity($scope, response);
      });
    }

    $scope.drawPolarity();
  })

  /* Communities controller */
  // .controller('communitiesController', function ($scope, $location, escuchaAPI, selection, sigmaSingleton, drawers, helpers) {
  //   selection.updateFromQueryString($location.search());

  //   $scope.start = selection.start;
  //   $scope.end = selection.end;

  //   $scope.sigmaGraph = {
  //     nodes: [],
  //     edges: []
  //   }
  //   $scope.zoomMin = 1 / 32;
  //   $scope.numNodes = 1000;

  //   $scope.searched = '';
  //   $scope.search_index = 0;
  //   $scope.search_results = [];
  //   $scope.search_result_text = '';

  //   $('.input-daterange[readonly!="True"]').datepicker(helpers.dateinputOptions);

  //   $scope.showNodesDropdown = function ($event) {
  //     $('.dropdown-toggle').dropdown()
  //     $event.preventDefault();
  //   }

  //   $scope.searchUser = function () {
  //     $scope.search_results = [];
  //     $scope.search_index = 0;

  //     if ($scope.searched != '') {
  //       var nodes = sigmaSingleton.instance.graph.nodes();
  //       for (var i = 0; i < nodes.length; i++) {
  //         if (nodes[i].label.match(helpers.make_pattern($scope.searched))) {
  //           $scope.search_results.push(nodes[i]);
  //         }
  //       }
  //     }

  //     if ($scope.searched != '' || $scope.search_results.length > 0) {
  //       sigmaSingleton.instance.camera.goTo({
  //         x: $scope.search_results[0]["read_cam0:x"],
  //         y: $scope.search_results[0]["read_cam0:y"],
  //         ratio: $scope.zoomMin,
  //       });
  //       if ($scope.search_results.length > 1) {
  //         $scope.search_result_text = "1 de " + $scope.search_results.length + " resultados";
  //       } else {
  //         $scope.search_result_text = "1 resultado";
  //       }

  //     } else {
  //       BootstrapDialog.alert({
  //         title: 'Buscar usuario',
  //         message: 'No se encontraron resultados.',
  //       });
  //     }
  //   }

  //   $scope.changeFocus = function (inc) {
  //     if ($scope.search_index + inc >= 0 && $scope.search_index + inc < $scope.search_results.length) {
  //       $scope.search_index += inc;

  //       sigmaSingleton.instance.camera.goTo({
  //         x: $scope.search_results[$scope.search_index]["read_cam0:x"],
  //         y: $scope.search_results[$scope.search_index]["read_cam0:y"],
  //         ratio: $scope.zoomMin,
  //       });
  //       if ($scope.search_results.length > 1) {
  //         $scope.search_result_text = ($scope.search_index + 1) + " de " + $scope.search_results.length + " resultados";
  //       }
  //     }
  //   }

  //   $scope.toggleEdges = function () {
  //     sigmaSingleton.instance.graph.edges().forEach(function (e) {
  //       e.hidden = !e.hidden;
  //     })
  //     window.dispatchEvent(new Event('resize'));
  //     if ($('#show_links_button').hasClass('active')) {
  //       $('#show_links_button').removeClass('active')
  //     } else {
  //       $('#show_links_button').addClass('active');
  //     }
  //     $('#show_links_button').blur();
  //   }

  //   $scope.toggleFullscreen = function () {
  //     $("#graph").toggleClass("fullscreen");
  //     $("#graph-container").toggleClass("fullscreen");

  //     window.dispatchEvent(new Event('resize'));

  //     var span = $('#full-screen-button').children(":first");
  //     if ($(span).hasClass('glyphicon-resize-full')) {
  //       $(span).removeClass('glyphicon-resize-full');
  //       $(span).addClass('glyphicon-resize-small');
  //     } else {
  //       $(span).removeClass('glyphicon-resize-small');
  //       $(span).addClass('glyphicon-resize-full');
  //     }
  //   }

  //   $scope.changeStartDate = function () {
  //     $scope.drawGraph();
  //   }

  //   $scope.changeNumNodes = function (numNodes) {
  //     $scope.numNodes = numNodes;
  //     $scope.drawGraph();
  //   }

  //   $scope.drawGraph = function () {
  //     escuchaAPI.getGraph(selection.apiterms, selection.region, $scope.start, $scope.end, $scope.numNodes).success(function (response) {
  //       drawers.drawGraph($scope, response);
  //     });
  //   }

  //   $scope.drawGraph();
  // })

  /* Historics controller */
  .controller('historicsController', function ($scope, $location, escuchaAPI, selection, sigmaSingleton, drawers, helpers) {
    selection.updateFromQueryString($location.search());

    // $scope.start = (selection.start == '') ? '1/12/2013' : selection.start;
    $scope.start = '01/12/2013'
    // $scope.end = (selection.end == '') ? helpers.dateToStr(new Date()) : selection.end;
    $scope.end = '31/12/2018'
    $scope.terms = selection.terms;
    $scope.region = selection.region;

    $scope.drawWeeklyCloud = function () {
      /* This function has to be uncommented once the backend is implemented */
      // escuchaAPI.getWeeklyCloud(selection.terms, selection.region, $scope.start, $scope.end).success(function (response) {
      //   drawers.drawWeeklyCloud($scope, response);
      // });
      
      /* This funtions have to be removed once the backend is implemented */
      response = escuchaAPI.getWeeklyCloud($scope.terms, $scope.region, $scope.start, $scope.end);
      drawers.drawWeeklyCloud($scope, response, escuchaAPI, helpers);
    }

    $scope.drawWeeklyCloud()

    $scope.cloudType = function(type) {console.log(type)
    switch (type) {
      case 'color':
          $(".swiper-container-cloud").css("filter", 'grayscale(0)' ).css("display","flex")
          $(".swiper-container-table").css("display","none")
          
        break;
      case 'grayscale':
          $(".swiper-container-cloud").css("filter", 'grayscale(1)').css("display","flex")
        break;
      case 'table':
          $(".swiper-container-cloud").css("display","none")
          $(".swiper-container-table").css("display","table-caption")
        break;
    
      default:
        break;
    }}
  })

  /* Subscription controller */
  // .controller('subscribeController', function ($scope, $location, settings, escuchaAPI, subscriptionsAPI, selection) {
  //   $scope.regions = [{ 'id': '*', 'label': 'TODO ARAGÓN' }];
  //   $scope.email = '';
  //   $scope.password = '';
  //   $scope.password2 = '';

  //   $scope.error = '';

  //   // Get the user subscriptions
  //   subscriptionsAPI.get_subscriptions().success(function (response) {
  //     $scope.subscriptions = response.subscriptions;
  //     if ($location.search().fromSearch == 1) {
  //       // Add the current search
  //       $scope.subscriptions.push({ 'name': '', 'region': selection.region, 'terms': selection.terms })
  //     }
  //   }).error(function (response) {
  //     BootstrapDialog.alert({
  //       title: 'Sucedió un error',
  //       message: 'No ha sido posible recoger la información de tus suscripciones.',
  //       type: BootstrapDialog.TYPE_DANGER,
  //       callback: function () {
  //         $location.path('/main');
  //         $scope.$apply(); // Bootstrap modal delay
  //       }
  //     });
  //   });

  //   escuchaAPI.getMetadata().success(function (response) {
  //     for (i = 0; i < response.regions.length; i++) {
  //       $scope.regions.push({ 'id': response.regions[i], 'label': response.regions[i] });
  //     }
  //   });

  //   $scope.addTerm = function (idx) {
  //     var subs = $scope.subscriptions[idx];
  //     if (subs.terms.length < 10) {
  //       subs.terms.push('');
  //     }
  //   };

  //   $scope.removeTerm = function (idx, tidx) {
  //     var subs = $scope.subscriptions[idx];
  //     if (subs.terms.length > 1) {
  //       subs.terms.splice(tidx, 1);
  //     }
  //   };

  //   $scope.addSubscription = function () {
  //     if ($scope.subscriptions.length < settings.MAX_SUBSCRIPTIONS) {
  //       $scope.subscriptions.push({ 'name': '', 'region': '*', 'terms': [''] });
  //     }
  //   }

  //   $scope.removeSubscription = function (idx) {
  //     if ($scope.subscriptions.length > 0) {
  //       $scope.subscriptions.splice(idx, 1);
  //     }
  //   }

  //   $scope.goBack = function () {
  //     $location.path('/main');
  //   }

  //   $scope.subscribe = function () {
  //     subscriptionsAPI.subscribe($scope.subscriptions)
  //       .success(function (response) {
  //         BootstrapDialog.alert({
  //           title: 'Suscripciones guardada',
  //           message: 'Suscripciones guardadas con éxito.',
  //           callback: function () {
  //             $location.path('/main');
  //             $scope.$apply(); // Bootstrap modal delay
  //           }
  //         });
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }

  //   $scope.passwordChange = function () {
  //     $location.path('/password_change');
  //   }

  //   $scope.logout = function () {
  //     subscriptionsAPI.logout();
  //     $location.path('/main');
  //   }

  //   $scope.cancelSubscription = function () {
  //     BootstrapDialog.confirm({
  //       title: 'Cancelar suscripción',
  //       message: '¿Estás seguro de que deseas cancelar tu suscripción a los informes de Aragón Open SocialData?',
  //       type: BootstrapDialog.TYPE_WARNING,
  //       btnCancelLabel: 'Cancelar',
  //       btnOKLabel: 'Aceptar',
  //       callback: function (result) {
  //         if (result) {
  //           subscriptionsAPI.cancel_subscription()
  //             .success(function (response) {
  //               BootstrapDialog.alert({
  //                 title: 'Suscripción cancelada',
  //                 message: 'Suscripción cancelada con éxito.',
  //                 callback: function () {
  //                   $location.path('/main');
  //                   $scope.$apply(); // Bootstrap modal delay
  //                 }
  //               });
  //             })
  //             .error(function (response) {
  //               $scope.error = response.error;
  //             });
  //         }
  //       }
  //     });
  //   }
  // })

  /* Login controller */
  // .controller('loginController', function ($scope, $location, subscriptionsAPI) {
  //   $scope.email = '';
  //   $scope.password = '';

  //   $scope.error = '';

  //   if (subscriptionsAPI.is_logged()) {
  //     // Redirect if logged
  //     $location.path('/subscribe');
  //   }

  //   $scope.goBack = function () {
  //     $location.path('/main');
  //   }

  //   $scope.login = function () {
  //     subscriptionsAPI.login($scope.email, $scope.password)
  //       .success(function (response) {
  //         $location.path('/subscribe');
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }
  // })

  /* Register controller */
  // .controller('registerController', function ($scope, $location, subscriptionsAPI) {
  //   $scope.email = '';
  //   $scope.password = '';
  //   $scope.password2 = '';

  //   $scope.error = '';

  //   if (subscriptionsAPI.is_logged()) {
  //     // Redirect if logged
  //     $location.path('/subscribe');
  //   }

  //   $scope.goBack = function () {
  //     $location.path('/main');
  //   }

  //   $scope.register = function () {
  //     if ($scope.password != $scope.password2) {
  //       $scope.error = 'Las contraseñas no coinciden';
  //       return;
  //     }
  //     subscriptionsAPI.register($scope.email, $scope.password)
  //       .success(function (response) {
  //         BootstrapDialog.alert({
  //           title: 'Registro completado',
  //           message: 'Te has registrado con éxito.',
  //           callback: function () {
  //             $location.path('/login');
  //             $scope.$apply(); // Bootstrap modal delay
  //           }
  //         });
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }
  // })

  /* Password change controller */
  // .controller('passwordChangeController', function ($scope, $location, subscriptionsAPI) {
  //   $scope.old_password = '';
  //   $scope.new_password = '';
  //   $scope.new_password2 = '';

  //   $scope.error = '';

  //   $scope.goBack = function () {
  //     $location.path('/subscribe');
  //   }

  //   $scope.change = function () {
  //     if ($scope.new_password != $scope.new_password2) {
  //       $scope.error = 'Las contraseñas no coinciden';
  //       return;
  //     }
  //     subscriptionsAPI.passwordChange($scope.old_password, $scope.new_password)
  //       .success(function (response) {
  //         BootstrapDialog.alert({
  //           title: 'Contraseña cambiada',
  //           message: 'Contraseña cambiada con éxito.',
  //           callback: function () {
  //             $location.path('/subscribe');
  //             $scope.$apply(); // Bootstrap modal delay
  //           }
  //         });
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }
  // })

  /* Password reset controller */
  // .controller('passwordResetController', function ($scope, $location, subscriptionsAPI) {
  //   $scope.email = '';

  //   $scope.error = '';

  //   if (subscriptionsAPI.is_logged()) {
  //     // Redirect if logged
  //     $location.path('/subscribe');
  //   }

  //   $scope.goBack = function () {
  //     $location.path('/login');
  //   }

  //   $scope.submit = function () {
  //     subscriptionsAPI.passwordReset($scope.email)
  //       .success(function (response) {
  //         BootstrapDialog.alert({
  //           title: 'Mensaje enviado',
  //           message: 'Se le ha enviado un correo electrónico con las indicaciones a seguir para cambiar su contraseña.',
  //           callback: function () {
  //             $location.path('/main');
  //             $scope.$apply(); // Bootstrap modal delay
  //           }
  //         });
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }
  // })

  /* Password reset confirm controller */
  // .controller('passwordResetConfirmController', function ($scope, $location, subscriptionsAPI) {
  //   $scope.new_password = '';
  //   $scope.new_password2 = '';

  //   $scope.error = '';

  //   if (subscriptionsAPI.is_logged()) {
  //     // Redirect if logged
  //     $location.path('/subscribe');
  //   }

  //   $scope.t = ($location.search().t !== undefined) ? $location.search().t : '';

  //   $scope.goBack = function () {
  //     $location.path('/login');
  //   }

  //   $scope.change = function () {
  //     if ($scope.new_password != $scope.new_password2) {
  //       $scope.error = 'Las contraseñas no coinciden';
  //       return;
  //     }
  //     subscriptionsAPI.passwordResetConfirm($scope.t, $scope.new_password)
  //       .success(function (response) {
  //         BootstrapDialog.alert({
  //           title: 'Contraseña cambiada',
  //           message: 'Contraseña cambiada con éxito.',
  //           callback: function () {
  //             $location.path('/login');
  //             $scope.$apply(); // Bootstrap modal delay
  //           }
  //         });
  //       })
  //       .error(function (response) {
  //         $scope.error = response.error;
  //       });
  //   }
  // });
