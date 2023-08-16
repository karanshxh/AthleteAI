import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

const loader = new FBXLoader();

const scene = new THREE.Scene();

let example = new THREE.Object3D();

loader.load( 'website2/static/deep_motion_vids/TableTennis/TableTennis_Adult_Male_Alt.fbx', function (fbx) {
    scene.add( fbx.scene );
}, undefined, function ( error ) {
    console.error(error);
})