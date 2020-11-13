angular
  .module("aosd.controllers", [])

  /* Main controller */
  .controller("mainController", function (
    $scope,
    $location,
    settings,
    escuchaAPI,
    selection,
    helpers
  ) {
    $scope.region = selection.region;
    $scope.regions = [{ id: "*", label: "TODO ARAGÓN" }];
    $scope.start = selection.start;
    $scope.end = selection.end;

    $scope.choices = [];

    for (i = 0; i < selection.terms.length; i++) {
      $scope.choices.push({ id: i + 1, name: selection.terms[i] });
    }
    if (!selection.terms.length) $scope.choices.push({ id: 1, name: "*" });
    // Reset the last search
    selection.totals = null;

    $scope.invalid_dates = "";
    $scope.termsList = sessionStorage.getItem("terms")
      ? sessionStorage.getItem("terms")
      : $scope.choices[0].name;
    sessionStorage.removeItem("terms");

    $('.input-daterange[readonly!="True"]').datepicker(
      helpers.dateinputOptions
    );

    escuchaAPI.getMetadata().success(function (response) {
      $scope.regions.push({
        id: "PROV HUESCA",
        label: "Huesca",
        tipo: "provincia",
      });
      $scope.regions.push({
        id: "PROV TERUEL",
        label: "Teruel",
        tipo: "provincia",
      });
      $scope.regions.push({
        id: "PROV ZARAGOZA",
        label: "Zaragoza",
        tipo: "provincia",
      });
      for (i = 0; i < response.regions.length; i++) {
        $scope.regions.push({
          id: response.regions[i],
          label: response.regions[i],
          tipo: "comarca",
        });
      }
      for (i = 0; i < response.mun.length; i++) {
        $scope.regions.push({
          id: "MUN " + response.mun[i],
          label: response.mun[i],
          tipo: "municipio",
        });
      }
    });

    $scope.validate_dates = function () {
      if ($scope.start == "" || $scope.end == "") {
        return true;
      } else {
        dstart = helpers.strToDate($scope.start);
        dend = helpers.strToDate($scope.end);
        return dstart <= dend;
      }
    };

    $scope.search_inst = function () {
      // Validate
      if (!$scope.validate_dates()) {
        $scope.invalid_dates =
          "La fecha de inicio no puede ser mayor que la de fin.";
        return;
      }

      $scope.choices = $scope.termsList ? $scope.termsList.split(" ") : "";

      selection.region = $scope.region;
      selection.start = $scope.start;
      selection.end = $scope.end;
      selection.terms = [];
      for (i = 0; i < $scope.choices.length; i++) {
        var q = $scope.choices[i] ? $scope.choices[i] : "*";
        if (selection.terms.indexOf(q) == -1) {
          selection.terms.push(q);
        }
      }

      var termsFormated = "";
      for (i = 0; i < selection.terms.length; i++) {
        if (i == selection.terms.length - 1) {
          termsFormated += selection.terms[i];
        } else {
          termsFormated += selection.terms[i] + " ";
        }
      }

      sessionStorage.setItem("terms", termsFormated);

      $location.path('/general_inst').search({
        region: selection.region,
        start: selection.start,
        end: selection.end,
        term: selection.terms,
        enlista: true,
      });
    };
  })

  /* Controller of general Page */
  .controller("generalController", function (
    $scope,
    $location,
    settings,
    escuchaAPI,
    selection,
    helpers
  ) {
    selection.updateFromQueryString($location.search());

    if (_.isEmpty($location.search())) {
      $location.path("/general_inst").hash("").search({
        region: "*",
        start: "",
        end: "",
        term: "*",
        enlista: true,
      });
      return;
    }
  })

  /* Controller for the search bar and info */
  .controller("searchController", function (
    $scope,
    settings,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    $scope.region = selection.region == "*" ? "Todo Aragón" : selection.region;
    $scope.start = selection.start == "" ? "1/12/2013" : selection.start;
    $scope.end =
      selection.end == "" ? helpers.dateToStr(new Date()) : selection.end;
    $scope.terms = selection.terms;
  })

  /* Controller for the search charts */
  .controller("searchChartController", function (
    $scope,
    settings,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    $scope.drawTotals = function () {
      if (selection.totals === null) {
        escuchaAPI
          .getTotals(
            selection.apiterms,
            selection.region,
            selection.start,
            selection.end
          )
          .success(function (response) {
            selection.totals = response;
            drawers.drawTotals($scope, selection.totals);
          });
      } else {
        drawers.drawTotals($scope, selection.totals);
      }
    };

    $scope.drawTotals();
  })

  /* SideNav Inst controller */
  .controller("sidenavInstController", function ($scope, $location, selection) {
    $scope.isActive = function (path) {
      var currentPath = $location.path().split("/")[1];
      if (currentPath.indexOf("?") !== -1) {
        currentPath = currentPath.split("?")[0];
      }
      return currentPath === path.split("/")[1];
    };

    $scope.moveTo = function (path) {
      $location.path(path).hash("").search({
        region: selection.region,
        start: selection.start,
        end: selection.end,
        term: selection.terms,
        enlista: selection.enlista,
      });
    };

    $scope.scrollTo = function (id) {
      $location.hash(id);
      // $anchorScroll();
    };
  })

  /* Evolution controller */
  .controller("evolutionController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    selection.updateFromQueryString($location.search());

    $scope.drawEvolutionTotal = function () {
      escuchaAPI
        .getEvolution(
          selection.apiterms,
          selection.region,
          selection.start,
          selection.end
        )
        .success(function (response) {
          drawers.drawEvolutionTotal($scope, response);
        });
    };

    $scope.drawEvolutionTotal();
  })

  /* Heatmap controller */
  .controller("heatmapController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    selection.updateFromQueryString($location.search());

    var raster = new ol.layer.Tile({
      source: new ol.source.OSM(),
    });

    var map = new ol.Map({
      layers: [raster],
      target: "map",
      view: new ol.View({
        center: ol.proj.transform(
          [-0.8833333, 41.6333333],
          "EPSG:4326",
          "EPSG:3857"
        ),
        zoom: 5,
      }),
    });

    var ALL_TERMS = "Todos los de la lista";

    $scope.change_terms = [ALL_TERMS];
    $scope.change_terms = $scope.change_terms.concat(selection.terms);
    $scope.change_terms_selected = ALL_TERMS;

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
      $scope.drawMap();
    };

    $scope.showLastItems = function () {
      if ($scope.markers_active) {
        $scope.markers = [];
        $scope.markers_items = {};
      } else {
        escuchaAPI
          .getLastItems(
            $scope.partial_terms,
            selection.region,
            selection.start,
            selection.end,
            0,
            true
          )
          .success(function (response) {
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
                  icon: "/static/public/socialdata/img/msg-icon.png",
                },
              };
              $scope.markers.push(marker);
              $scope.markers_items[item.id] = {
                id: item.id,
                title: item.title,
                description: item.description,
                author: item.author,
                source: item.source,
                published_on: item.published_on,
              };
            }
          });
      }
      $scope.markers_active = !$scope.markers_active;
    };

    $scope.showMessage = function (item_id) {
      var item = $scope.markers_items[item_id];
      BootstrapDialog.alert({
        title:
          "Mensaje del usuario <b>" +
          item.author +
          "</b> en <b>" +
          helpers.titleCase(item.source) +
          "</b>",
        message:
          (item.title === null ? "" : item.title + "\n\n") +
          item.description +
          "\n\n<small><i>" +
          item.published_on +
          "</i></small>",
      });
    };

    $scope.map.heatLayerCallback = function (heatLayer) {
      heatLayer.setOptions(helpers.heatmapOptions);
      $scope.map.heatLayer = heatLayer;
      $scope.drawMap();
    };

    $scope.drawMap = function () {
      escuchaAPI
        .getGeogrid(
          $scope.partial_terms,
          selection.region,
          selection.start,
          selection.end,
          $scope.map_weight
        )
        .success(function (response) {
          drawers.drawMap($scope, response);
        });
    };
    // CALL FOR THE FIRST TIME
    $scope.drawMap();

    $scope.changeHeatmapWeight = function () {
      $scope.drawMap();
    };
  })

  /* Top Hashtags controller */
  .controller("topHashtagsController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    $scope.top_hashtags = [];
    $scope.top_authors = [];
    $scope.top_mentions = [];

    $scope.drawTops = function () {
      escuchaAPI
        .getTops(
          selection.apiterms,
          selection.region,
          selection.start,
          selection.end
        )
        .success(function (response) {
          drawers.drawHemicycles($scope, response);
          $scope.top_hashtags = response.top_hashtags;
          $scope.top_authors = response.top_authors;
          $scope.top_mentions = response.top_mentions;
        });
    };

    $scope.drawTops();
  })

  /* Last messages controller */
  .controller("lastMessagesController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    $scope.last_items = [];
    $scope.last_items_page = 0;

    $scope.hemicycle_hashtags = { title: { text: "" } };
    $scope.hemicycle_mentions = { title: { text: "" } };

    $scope.moreItems = function () {
      $scope.last_items_page = $scope.last_items_page + 1;
      escuchaAPI
        .getLastItems(
          selection.apiterms,
          selection.region,
          selection.start,
          selection.end,
          $scope.last_items_page
        )
        .success(function (response) {
          $scope.last_items = $scope.last_items.concat(response.last_items);
        });
    };

    $scope.drawLastItems = function () {
      escuchaAPI
        .getLastItems(
          selection.apiterms,
          selection.region,
          selection.start,
          selection.end
        )
        .success(function (response) {
          $scope.last_items = response.last_items;
        });
    };

    $scope.drawLastItems();
  })

  /* Polarity controller */
  .controller("polarityController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    drawers,
    helpers
  ) {
    selection.updateFromQueryString($location.search());

    $scope.polarity_pos = [{ Nivel: 0 }];
    $scope.polarity_pos_cols = [{ id: "Nivel", type: "gauge" }];

    $scope.polarity_neg = [{ Nivel: -1 }];
    $scope.polarity_neg_cols = [{ id: "Nivel", type: "gauge" }];

    $scope.terms_polarity = [];

    $scope.polarityColor = function (color, d) {
      if (d.value) {
        if (d.value == 0) return "#F97600";
        else return d.value < 0 ? "#A52A2A" : "#4682B4";
      } else {
        return null;
      }
    };

    $scope.polarityTooltip = function (d) {
      return "Nivel de polaridad";
    };

    $scope.drawPolarity = function () {
      escuchaAPI
        .getPolarity(
          selection.apiterms,
          selection.region,
          selection.start,
          selection.end
        )
        .success(function (response) {
          drawers.drawPolarity($scope, response);
        });
    };

    $scope.drawPolarity();
  })

  /* Historics cloud controller */
  .controller("cloudController", function (
    $scope,
    $location,
    escuchaAPI,
    selection,
    sigmaSingleton,
    drawers,
    helpers
  ) {
    selection.updateFromQueryString($location.search());

    // $scope.start = (selection.start == '') ? '1/12/2013' : selection.start;
    $scope.start = "01/12/2013";
    // $scope.end = (selection.end == '') ? helpers.dateToStr(new Date()) : selection.end;
    $scope.end = "31/12/2018";
    $scope.terms = selection.terms;
    $scope.region = selection.region;

    $scope.drawWeeklyCloud = function () {
      response = escuchaAPI.getWeeklyCloud(
        $scope.terms,
        $scope.region,
        $scope.start,
        $scope.end
      );
      drawers.drawWeeklyCloud($scope, response, escuchaAPI, helpers);
    };

    $scope.drawWeeklyCloud();

    $scope.cloudType = function (type) {
      switch (type) {
        case "color":
          $(".swiper-container-cloud")
            .css("filter", "grayscale(0)")
            .css("display", "flex");
          $(".swiper-container-table").css("display", "none");

          break;
        case "grayscale":
          $(".swiper-container-cloud")
            .css("filter", "grayscale(1)")
            .css("display", "flex");
          break;
        case "table":
          $(".swiper-container-cloud").css("display", "none");
          $(".swiper-container-table").css("display", "list-item");
          break;

        default:
          break;
      }
    };
  });
