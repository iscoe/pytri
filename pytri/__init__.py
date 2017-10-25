#!/usr/bin/env python3
"""
Copyright 2017 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import uuid
import json

import requests
from IPython.display import Javascript, HTML, display
import networkx as nx
from networkx.readwrite import json_graph


__version__ = "0.0.1"


class pytri:
    """
    The global class for Pytri visualization.

    .
    """

    def __init__(self):
        """
        Create a new visualizer frame.

        Arguments:
            None

        """
        scripts = [
            "https://threejs.org/examples/js/controls/TrackballControls.js",
        ]

        threesrc = requests.get("https://threejs.org/build/three.js").text.split('\n')
        threesrc = threesrc[6:-2]

        js = "exports = window.THREE || {}; " + "\n".join(threesrc) + "window.THREE = exports;"

        for script in scripts:
            js += requests.get(script).text.strip()

        with open("./substrate.min.js", 'r') as fh:
            js += ";\n\n" + fh.read().strip()

        self.js = js
        self.uid = str(uuid.uuid4())

    def show(self):
        """
        Render the frame to the Jupyter notebook.

        Arguments:
            None

        """
        display(HTML(
            "<script>{}</script>".format(self.js) +
            "<div id='pytri-target-{}'></div>".format(self.uid) + """
            <script>
            V = V || {}
            if (typeof V['"""+self.uid+"""'] === "undefined") {
                V['"""+self.uid+"""'] = new Visualizer({
                    targetElement: "pytri-target-"""+self.uid+"""",
                    backgroundColor: new window.THREE.Color(0xffffff),
                    renderLayers: {
                        // None yet!
                    }
                });
            }
            V['"""+self.uid+"""'].triggerRender();
            V['"""+self.uid+"""'].resize(undefined, 400)
            </script>
        """))

    def remove_layer(self, name):
        """
        Remove a layer by name.

        Arguments:
            name (str)

        Returns:
            None

        """
        display(Javascript("""
            V['"""+self.uid+"""'].removeLayer('{}')
        """.format(name)))

    def axes(self):
        """
        Add axes to the visualization.

        Arguments:
            None

        Returns:
            None

        """
        display(Javascript("""
            class AxisLayer extends Layer {
                requestInit(scene) {
                    let axes = new window.THREE.AxisHelper(5);
                    this.children.push(axes)
                    scene.add(axes)
                }
            }
            if (typeof V['"""+self.uid+"""'] === 'undefined') {
                V = V || {};
                V['"""+self.uid+"""'] = new Visualizer({
                    targetElement: "pytri-target-"""+self.uid+"""",
                    backgroundColor: new window.THREE.Color(0xffffff),
                    renderLayers: {
                        // None yet!
                    }
                });
            }
            V['"""+self.uid+"""'].addLayer('axes', new AxisLayer())
        """))

    def scatter(self, data, r=0.15, c=0x00babe):
        """
        Add a 3D scatter to the scene.

        Arguments:
            data (np.ndarray)
            r (float | list)
            c (hex | list)

        Returns:
            None

        """
        d = data.tolist()
        _js = ("""
        
        class ScatterLayer extends Layer {
            constructor(opts) {
                super(opts);

                this.setData = this.setData.bind(this);
                this.radius = opts.radius || 0.15;
                this.colors = opts.colors || 0x00babe;
                if (typeof(this.colors) == "number") {
                    this.c_array = false;
                } else {
                    this.c_array = true;
                }
                this.setData(opts.data);
            }

            setData(data) {
                this.data = data;
                this.requestInit;
            }

            requestInit(scene) {
                for (let i = 0; i < this.data.length; i++) {
                    let sph = new window.THREE.Mesh(
                        new window.THREE.SphereGeometry(this.radius, 6, 6),
                        new window.THREE.MeshBasicMaterial({
                            color: this.c_array ? this.colors[i] : this.colors
                        })
                    );
                    sph.position.set(...this.data[i]);
                    this.children.push(sph)
                    scene.add(sph)

                }
            }
        }
        """ + """
        if (typeof V['"""+self.uid+"""'] === 'undefined') {
            V = V || {};
            V['"""+self.uid+"""'] = new Visualizer({
                targetElement: "pytri-target-"""+self.uid+"""",
                backgroundColor: new window.THREE.Color(0xffffff),
                renderLayers: {
                    // None yet!
                }
            });
        }
        V['"""+self.uid+"""'].addLayer('scatter', new ScatterLayer({{
            data: {},
            radius: {},
            colors: {}
        }}))
        """.format(
            json.dumps(d),
            r,
            c
        ))
        display(Javascript(_js))


    def graph(self, data, r=0.15, c=0xbabe00):
        """
        Add a graph to the visualizer.

        Arguments:
            data (networkx.graph)
            r (float | list)
            c (float | list)

        Returns:
            None

        """
        if isinstance(data, nx.Graph):
            data = json_graph.node_link_data(data)
        
        if type(next(iter(data['nodes']))['pos']) is dict:
            dict_pos = 1
        elif type(next(iter(data['nodes']))['pos']) is tuple:
            dict_pos = 0
        _js = ("""
        class GraphLayer extends Layer {
            constructor(opts) {
                super(opts);

                this.setData = this.setData.bind(this);
                this.radius = opts.radius || 0.15;
                this.colors = opts.colors || 0x00babe;
                if (typeof(this.colors) == "number") {
                    this.c_array = false;
                } else {
                    this.c_array = true;
                }
                this.setData(opts.data);
                this.attr_dict = false;
                this.attr_tup = false;
                if (opts.dict_pos) {
                    this.attr_dict = true;
                } else if (!opts.dict_pos) {
                    this.attr_tup = true;
                }
            }

            setData(data) {
                this.data = data;
                this.requestInit;
            }

            requestInit(scene) {
                for (let i = 0; i < this.data.nodes.length; i++) {
                    let sph = new window.THREE.Mesh(
                        new window.THREE.SphereGeometry(this.radius, 6, 6),
                        new window.THREE.MeshBasicMaterial({
                            color: this.c_array ? this.colors[i] : this.colors
                        })
                        );
                    if (this.attr_dict) {
                        let n = this.data.nodes[i].pos
                        sph.position.set(n.x, n.y, n.z);
                    } else if (this.attr_tup) {
                        console.log(this.data.nodes[i])
                        sph.position.set(...this.data.nodes[i].pos)
                    }
                    
                    this.children.push(sph)
                    scene.add(sph)
                }

                for (var i = 0; i < this.data.links.length; i++) {
                    var edgeGeometry = new window.THREE.Geometry();
                    var edgeMaterial = new window.THREE.LineBasicMaterial({
                        color: 0xbabe00 * (this.data.links[i].weight || 1),
                        transparent: true,
                        opacity: this.data.links[i].weight || 1,
                        linewidth: this.data.links[i].weight || 1,
                    });
                    if (this.attr_dict) {
                        let sn = this.data.nodes[this.data.links[i].source].pos
                        let tn = this.data.nodes[this.data.links[i].target].pos
                        edgeGeometry.vertices.push(
                            new window.THREE.Vector3(sn.x, sn.y, sn.z),
                            new window.THREE.Vector3(tn.x, tn.y, tn.z)
                        );
                    } else if (this.attr_tup) {
                        console.log(this.data.nodes[this.data.links[i].source].pos)
                        console.log(this.data.nodes[this.data.links[i].target].pos)
                        edgeGeometry.vertices.push(
                            new window.THREE.Vector3(...this.data.nodes[this.data.links[i].source].pos),
                            new window.THREE.Vector3(...this.data.nodes[this.data.links[i].target].pos)
                        );
                    }
                    var line = new window.THREE.Line(edgeGeometry, edgeMaterial);
                    this.children.push(line);
                    scene.add(line);
                }
            }
        }
        """ + """
        if (typeof V['"""+self.uid+"""'] === 'undefined') {
            V = V || {};
            V['"""+self.uid+"""'] = new Visualizer({
                targetElement: "pytri-target-"""+self.uid+"""",
                backgroundColor: new window.THREE.Color(0xffffff),
                renderLayers: {
                    // None yet!
                }
            });
        }
        V['"""+self.uid+"""'].addLayer('graph', new GraphLayer({{
            data: {},
            radius: {},
            colors: {},
            dict_pos: {}
        }}))
        """.format(
            json.dumps(data),
            r,
            c,
            dict_pos
        ))
        display(Javascript(_js))
