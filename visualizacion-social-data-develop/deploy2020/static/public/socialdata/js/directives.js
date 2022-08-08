angular
  .module("aosd.directives", [])

  /* Logo */
  .directive("logo", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/logo.html",
    };
  })

  /* Side nav inst menu directive */
  .directive("sidenavinstsect", function () {
    return {
      restrict: "E",
      templateUrl:
        "/static/public/socialdata/html/partials/sidenavInstSect.html",
      controller: "sidenavInstController",
    };
  })

  /* Selection the statistics institutional section */
  .directive("statsinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/statsInstSect.html",
      controller: "statsController",
    };
  })
  /* Selection the top hashtags institutional section */
  .directive("tophashinstsect", function () {
    return {
      restrict: "E",
      templateUrl:
        "/static/public/socialdata/html/partials/topHashInstSect.html",
      controller: "topHashtagsController",
    };
  })
  /* Selection the hashtags institutional section */
  .directive("hashinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/hashInstSect.html",
      controller: "topHashtagsController",
    };
  })
  /* Selection the last messages institutional section */
  .directive("lastmessinstsect", function () {
    return {
      restrict: "E",
      templateUrl:
        "/static/public/socialdata/html/partials/lastMessInstSect.html",
      controller: "lastMessagesController",
    };
  })

  /* Evolution institutional section */
  .directive("evoinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/evoInstSect.html",
      controller: "evolutionController",
    };
  })

  /* Heat map institutional section */
  .directive("heatinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/heatInstSect.html",
      controller: "heatmapController",
    };
  })

  /* Polarity institutional section */
  .directive("polinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/polInstSect.html",
      controller: "polarityController",
    };
  })

  /* Polarity institutional section */
  .directive("cloudinstsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/cloudInstSect.html",
      controller: "cloudController",
    };
  })

  /* Search section */
  .directive("searchsect", function () {
    return {
      restrict: "E",
      templateUrl: "/static/public/socialdata/html/partials/searchSect.html",
      //  controller: 'searchController',
    };
  })

  /* Search charts section */
  .directive("searchinfosect", function () {
    return {
      restrict: "E",
      templateUrl:
        "/static/public/socialdata/html/partials/searchInfoSect.html",
      controller: "searchController",
    };
  })

  /* Search charts section */
  .directive("searchchartsect", function () {
    return {
      restrict: "E",
      templateUrl:
        "/static/public/socialdata/html/partials/searchChartSect.html",
      controller: "searchChartController",
    };
  })

  // Directive for pie charts, pass in title and data only
  .directive("hcGaugeChart", function () {
    return {
      restrict: "E",
      template: "<div></div>",
      scope: {
        chartOrig: "=chart",
        title: "@",
        chart: "=",
      },
      link: function (scope, element) {
        console.log(scope);
        // Watches, to refresh the chart when its data change
        scope.$watch(
          "chartOrig",
          function () {
            scope.chart = angular.copy(scope.chartOrig);
            draw();
          },
          true
        ); // true is for deep object equality checking

        // $rootScope.$on("resizeMsg", function () {
        //   $timeout(function () {
        //     // Not always defined yet in IE so check
        //     if ($scope.chartWrapper) {
        //       draw();
        //     }
        //   });
        // });

        function draw() {
          Highcharts.chart(element[0], {
            chart: {
              type: "solidgauge",
              height: 400, // Necesary to work on firefox
            },

            title: null,

            pane: {
              center: ["26%", "45%"],
              // size: "100%",
              startAngle: -90,
              endAngle: 90,
              background: {
                backgroundColor:
                  Highcharts.defaultOptions.legend.backgroundColor || "#EEE",
                innerRadius: "55%",
                outerRadius: "90%",
                shape: "arc",
                // height: "100px",
                borderWidth: "1px",
              },
            },
            exporting: {
              enabled: false,
            },
            tooltip: {
              enabled: false,
            },

            // the value axis
            yAxis: {
              // stops: [
              //   [-0.5, "#55BF3B"], // green
              //   [0.5, "#DDDF0D"], // yellow
              //   [0.9, "#DF5353"], // red
              // ],
              lineWidth: 0,
              tickWidth: 0,
              minorTickInterval: null,
              tickAmount: 2,
              // title: {
              //   y: -70,
              // },
              labels: {
                y: 16,
              },
              min: -100,
              max: 100,
              title: {
                text: scope.chart.muestreo,
                y: 16,
              },
            },

            plotOptions: {
              solidgauge: {
                dataLabels: {
                  y: -5,
                  borderWidth: 0,
                  useHTML: true,
                },
              },
            },
            credits: {
              enabled: false,
            },

            series: [
              {
                name: scope.chart.muestreo,
                data: [
                  { y: scope.chart.end_value * 100, color: scope.chart.color },
                  { y: scope.chart.start_value * 100, color: "#eeeeee"},
                ],
                // colors: [scope.chart.color, "#eeeeee"],
                radius: '90%',
                innerRadius: '55%',
                borderColor: "#cfcfcf",
                borderWidth:1,
                dataLabels: {
                  format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:18px">' +
                    (scope.chart.start_value * 100).toFixed(1) +
                    "%  ↔ " +
                    (scope.chart.end_value * 100).toFixed(1) +
                    "%</span><br/>" +
                    '<span style="font-size:12px;opacity:0.4">Indica la '+ scope.chart.muestreo +' de los mensajes.</span>' +
                    "</div>",
                },
              },
            ],
          });
        }
      },
    };
  });
