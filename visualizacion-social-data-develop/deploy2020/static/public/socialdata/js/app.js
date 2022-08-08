var app = angular
  .module("aosd", [
    "aosd.controllers",
    "aosd.services",
    "aosd.directives",
    "aosd.filters",
    "ngRoute",
    "ngCookies",
    "ngScrollTo",
    "angular-loading-bar",
    "googlechart",
    "uiGmapgoogle-maps",
    "gridshore.c3js.chart",
    "highcharts-ng",
  ])
  .constant("settings", {
    // API_URL: "http://193.146.116.204:8003/aosd", // COMENT FOR PRODUCTION
    API_URL: "http://miv-aodfront-01.aragon.local:8004/aosd", // UNCOMENT FOR PRODUCTION
    MAX_SUBSCRIPTIONS: 10,
    MAX_TERMS: 10,
  })
  .config(function (
    $interpolateProvider,
    $httpProvider,
    $routeProvider,
    uiGmapGoogleMapApiProvider,
    cfpLoadingBarProvider
  ) {
    /*    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');*/

    $httpProvider.defaults.headers.common["X-Requested-With"] =
      "XMLHttpRequest";
    $httpProvider.defaults.xsrfCookieName = "csrftoken";
    $httpProvider.defaults.xsrfHeaderName = "X-CSRFToken";

    //disable IE ajax request caching
    $httpProvider.defaults.headers.common["Cache-Control"] = "no-cache";
    $httpProvider.defaults.headers.common["Pragma"] = "no-cache";

    $routeProvider
      .when("/general_inst", {
        templateUrl: "/static/public/socialdata/html/partials/genInst.html",
        controller: "generalController",
      })
      .when("/historics_inst", {
        templateUrl: "/static/public/socialdata/html/partials/histoInst.html",
        // controller: "historicsController",
      })
      .when("/about", {
        templateUrl: "/static/public/socialdata/html/partials/about.html",
        // controller: "aboutController",
      })
      .otherwise({ redirectTo: "/general_inst" });

    cfpLoadingBarProvider.includeSpinner = false;

    uiGmapGoogleMapApiProvider.configure({
      v: "3.17",
      libraries: "visualization",
    });
  })
  .run(function ($rootScope, $location, subscriptionsAPI) {
    var routesThatRequireAuth = ["/subscribe", "/password_change"];

    $rootScope.$on("$routeChangeStart", function (event, next, current) {
      // if route requires auth and user is not logged in
      var urlPath = $location.url().split("?")[0];
      if (
        routesThatRequireAuth.indexOf(urlPath) >= 0 &&
        !subscriptionsAPI.is_logged()
      ) {
        // redirect back to login
        $location.path("/login");
      }
    });
  });
