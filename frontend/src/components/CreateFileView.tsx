import { onMount } from 'solid-js';
import { apiClient } from '../lib/api';
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import MaplibreGeocoder from '@maplibre/maplibre-gl-geocoder';
import '@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css';

const geocodeEarthResults = async (config:any, endpoint: string) => {
    const likeCoordinates = /^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/;
    if (likeCoordinates.test(config.query)) {
      const pair = config.query.split(",");
      const lat = +pair[0];
      const lng = +pair[1];
      return {
        type: 'FeatureCollection',
        features: [{
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [lng,lat]
          },
          properties: {},
          place_name: `${lat},${lng}`
        }]
      }
    }

    const url = "https://api.geocode.earth/v1/" + endpoint +
                "?api_key=" + import.meta.env.PUBLIC_GEOCODE_EARTH_KEY +
                "&text=" + encodeURIComponent(config.query);
    const result = await fetch(url);
    const json = await result.json();
    json.features.forEach((f:any) => {
        const props = f.properties;
        f.place_name = props.label;
    });
    return json;
};

export default function CreateFileView() {
  onMount(() => {
    if (!apiClient.isAuthenticated()) {
      window.location.href = '/auth/login';
    }

    maplibregl.setRTLTextPlugin(
      "rtl-text.min.js",
      true,
    );

    const map = new maplibregl.Map({
      container: "map",
      style: `https://api.protomaps.com/styles/v5/light/en.json?key=` + import.meta.env.PUBLIC_PROTOMAPS_KEY
    });

    const geocoder = new MaplibreGeocoder(
          {
              getSuggestions: config => geocodeEarthResults(config, "autocomplete"),
              forwardGeocode: config => geocodeEarthResults(config, "search")
          },
          {
              maplibregl,
              showResultsWhileTyping: true,
              placeholder: "Search a city or address",
              marker: false,
              showResultMarkers: false,
              flyTo: {animate: false}
          }
      );
    
    map.addControl(geocoder, 'top-left');
  });


  return (
    <div class="card">
      <h1>Create File</h1>
      <div id="map" style="height: 400px; width: 400px"></div>
    </div>
  );
}
