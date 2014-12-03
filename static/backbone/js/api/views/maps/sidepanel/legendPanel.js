define(["marionette",
        "underscore",
        "jquery",
        "views/maps/sidepanel/filter",
        "views/maps/sidepanel/legendItem",
        "text!" + templateDir + "/sidepanel/legendPanelHeader.html"
    ],
    function (Marionette, _, $, DataFilter, LegendItem, legendPanelHeader) {
        'use strict';
        /**
         * A class that handles display and rendering of the
         * data panel and projects menu
         * @class DataPanel
         */
        var LegendPanel = Marionette.LayoutView.extend({
            /**
             * @lends localground.maps.views.DataPanel#
             */
            template: function () {
                return _.template(legendPanelHeader);
            },
            entries: [
                {
                    id: 1,
                    name: "Worms",
                    children: [
                        {
                            title: "At least 1 worm",
                            color: "#7075FF",
                            rule: "worms > 0"
                        },
                        {
                            title: "No worms",
                            color: "#F011D9",
                            rule: "worms = 0"
                        }
                    ]
                },
                {
                    id: 2,
                    name: "Soil Moisture",
                    children: [
                        {
                            title: "Moist soil",
                            color: "#428BCA",
                            rule: "moisture = 'moist'"
                        },
                        {
                            title: "Dry soil",
                            color: "#b7f081",
                            rule: "moisture = 'dry'"
                        }
                    ]
                },
                {
                    id: 3,
                    name: "Percolation Time",
                    children: [
                        {
                            title: "Fast percolation time (<= 30s)",
                            color: "#a2e6ef",
                            rule: "percolation <= 30"
                        },
                        {
                            title: "Medium percolation time (between 30 and 200s)",
                            color: "#19b8ca",
                            rule: "percolation > 30 and percolation <= 200"
                        },
                        {
                            title: "Slow percolation time (more than 200s)",
                            color: "#0e727e",
                            rule: "percolation > 200"
                        }
                    ]
                },
                {
                    id: 4,
                    name: "Pitfall Count",
                    children: [
                        {
                            title: "Less than 10 invertebrates",
                            color: "#5cee1e",
                            rule: "pitfall < 10"
                        },
                        {
                            title: "10 or more invertebrates",
                            color: "#3b9914",
                            rule: "pitfall >= 10"
                        }
                    ]
                }
            ],
            regions: {
                legend: "#legend-manager",
                dataFilter: "#data-filter"
            },
            /**
             * Initializes the dataPanel
             * @param {Object} opts
             */
            initialize: function (opts) {
                this.app = opts.app;
                this.opts = opts;
                opts.app.vent.on("new-collection-created", this.applyToCollection.bind(this));
                opts.app.vent.on("adjust-layout", this.resize.bind(this));
            },

            addLegendEntries: function () {
                var that = this,
                    selector;
                $.each(this.entries, function () {
                    selector = "legend_" + this.id;
                    that.$el.find('#legend-manager').append($('<div id="' + selector + '"></div>'));
                    that.addRegion(selector, '#' + selector);
                    this.app = that.app;
                    that[selector].show(new LegendItem(this));
                });
            },

            onShow: function () {
                this.addLegendEntries();
                this.dataFilter.show(new DataFilter(this.opts));
                this.resize();
            },

            applyToCollection: function (opts) {
                //console.log(opts.collection);
            },

            destroy: function () {
                this.remove();
            },

            resize: function () {
                this.$el.find('.pane-body').height($('body').height() - 140);
            }
        });
        return LegendPanel;
    });
