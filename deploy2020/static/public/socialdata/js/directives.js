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
  });
