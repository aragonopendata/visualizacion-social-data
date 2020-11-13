angular.module('aosd.directives', [])

  /* Sigma JS directive */
  // .directive('sigmajs', function(sigmaSingleton) {
  //   //over-engineered random id, so that multiple instances can be put on a single page
  //   var divId = 'sigmjs-dir-container-'+Math.floor((Math.random() * 999999999999))+'-'+Math.floor((Math.random() * 999999999999))+'-'+Math.floor((Math.random() * 999999999999));
  //   return {
  //     restrict: 'E',
  //     template: '<div id="'+divId+'" style="width: 100%;height: 100%;"></div>',
  //     scope: {
  //       graph: '=',
  //       width: '@',
  //       height: '@',
  //     },
  //     link: function (scope, element, attrs) {
  //       var zoomMax = 1;
  //       var zoomMin = 1/32;

  //       var s = new sigma({
  //         renderer: {
  //           container: document.getElementById(divId),
  //           type: 'canvas'
  //         },
  //         settings: {
  //           batchEdgesDrawing: true,
  //           hideEdgesOnMove: true,
  //           defaultNodeColor: "#ec5148",
  //           labelThreshold: 6.0,
  //           labelSize: "proportional",
  //           zoomMax: zoomMax,
  //           zoomMin: zoomMin,
  //           maxNodeSize: 12.0,
  //           minEdgeSize: 0.2,
  //           maxEdgeSize: 3,
  //           sideMargin: 100
  //         }
  //       });

  //       sigmaSingleton.instance = s;

  //       scope.$watch('graph', function(newVal,oldVal) {
  //         s.graph.clear();
  //         s.graph.read(scope.graph);
  //         s.refresh();
  //         if (s.graph.nodes.length < 5) {
  //           s.camera.goTo({x: s.camera.x, y: s.camera.y, ratio: zoomMax});
  //         }
  //       });

  //       scope.$watch('width', function(newVal,oldVal) {
  //         element.children().css("width",scope.width);
  //         s.refresh();
  //         window.dispatchEvent(new Event('resize')); //hack so that it will be shown instantly
  //       });

  //       scope.$watch('height', function(newVal,oldVal) {
  //         element.children().css("height",scope.height);
  //         s.refresh();
  //         window.dispatchEvent(new Event('resize'));//hack so that it will be shown instantly
  //       });

  //       element.on('$destroy', function() {
  //         s.graph.clear();
  //       });
  //     }
  //   };
  // })

  /* Logo */
  .directive('logo', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/logo.html',
    }
  })

  /* Side nav menu directive */
  // .directive('sidenav', function() {
  //   return {
  //     restrict: 'E',
  //     templateUrl: '/static/public/socialdata/html/partials/sidenav.html',
  //     controller: 'sidenavController',
  //   }
  // })

    /* Side nav inst menu directive */
  // .directive('sidenavinst', function() {
  //   return {
  //     restrict: 'E',
  //     templateUrl: '/static/public/socialdata/html/partials/sidenavInst.html',
  //     controller: 'sidenavInstController',
  //   }
  // })


  /* Selection help text */
  // .directive('selectionhelpinst', function() {
  //   return {
  //     restrict: 'E',
  //     templateUrl: '/static/public/socialdata/html/partials/selectionHelpInst.html',
  //     controller: 'selectionHelpController',
  //   }
  // })

  /* Selection help text */
  // .directive('selectionhelp', function() {
  //   return {
  //     restrict: 'E',
  //     templateUrl: '/static/public/socialdata/html/partials/selectionHelp.html',
  //     controller: 'selectionHelpController',
  //   }
  // })

/* NEW STRUCTURE */
  /* Side nav inst menu directive */
  .directive('sidenavinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/sidenavInstSect.html',
      controller: 'sidenavInstController',
    }
  })


  /* Selection the statistics institutional section */
  .directive('statsinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/statsInstSect.html',
      controller: 'statsController',
    }
  })
   /* Selection the top hashtags institutional section */
   .directive('tophashinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/topHashInstSect.html',
      controller: 'topHashtagsController',
    }
  })
   /* Selection the hashtags institutional section */
   .directive('hashinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/hashInstSect.html',
      controller: 'topHashtagsController',
    }
  })
   /* Selection the last messages institutional section */
   .directive('lastmessinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/lastMessInstSect.html',
      controller: 'lastMessagesController',
    }
  })

  /* Evolution institutional section */
  .directive('evoinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/evoInstSect.html',
      controller: 'evolutionController',
    }
  })
  
  /* Heat map institutional section */
  .directive('heatinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/heatInstSect.html',
      controller: 'heatmapController',
    }
  })
  
  /* Polarity institutional section */
  .directive('polinstsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/polInstSect.html',
      controller: 'polarityController',
    }
  })
  
  /* Search section */
  .directive('searchsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/searchSect.html',
      //  controller: 'searchController',
    }
  })

  /* Search charts section */
  .directive('searchinfosect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/searchInfoSect.html',
      controller: 'searchController',
    }
  })
  
  /* Search charts section */
  .directive('searchchartsect', function() {
    return {
      restrict: 'E',
      templateUrl: '/static/public/socialdata/html/partials/searchChartSect.html',
      controller: 'searchChartController',
    }
  });
