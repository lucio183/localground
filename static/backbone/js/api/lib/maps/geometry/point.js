define([], function() {
	/** 
     * Functions to help move from lat/lngs to GeoJSON
     * formats and vice versa
     * @class Point
     */
	localground.maps.geometry.Point = (function (opts) {
		
		/**
		 * Static method that converts a google.maps.Point
		 * into a GeoJSON Point object.
		 * @param {google.maps.LatLng} googlePoint
		 * A Google point object.
		 * @see See the Google <a href="https://developers.google.com/maps/documentation/javascript/reference#LatLng">google.maps.LatLng</a>
		 * documentation for more details.
		 * @returns a GeoJSON Point object
		 */
		this.getGeoJSON = function(latLng){
			return {
				type: 'Point',
				coordinates: [latLng.lng(), latLng.lat()]
			};
		};
		
		/**
		 * Static method that converts a GeoJSON Point into
		 * a google.maps.LatLng object.
		 * @param {GeoJSON Point} geoJSON
		 * A GeoJSON Point object
		 * @returns {google.maps.LatLng}
		 * A google.maps.LatLng object 
		 */
		this.getGoogleLatLng = function(geoJSON){
			return new google.maps.LatLng(
				geoJSON.coordinates[1],
				geoJSON.coordinates[0]
			);
		};
		
		//initialize the geolocation helper:
		initialize(opts);
	});
	return localground.maps.geometry.Point;
});