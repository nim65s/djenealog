/* found on https://www.cg.tuwien.ac.at/courses/Visualisierung2/HallOfFame/2014/Tofi/Homepage/codedoc/files/client.js.html */

/**
 * Server module
 *
 * @module server
 */

/**
 * The server file
 *
 * @class Server
 */

"use strict";

var app = require("http").createServer(handler)
  , io = require("socket.io").listen(app)
  , fs = require("fs")
  , sqlite3 = require("sqlite3").verbose()
  , db = "timenets.db";

app.listen(8069);

/**
 * Open the database
 *
 * @method openDb
 * @return opened database
 */
function openDb() {
  return new sqlite3.Database(db, sqlite3.OPEN_READWRITE, function() {
    console.log("Database opened");
  });
}

/**
 * Node.js/Socket.io webserver callback, serves files
 *
 * @method handler
 */
function handler (req, res) {
  var url = req.url;
  if (url === "/") {
    url = "/index.html";
  }

  fs.readFile(__dirname + url,
    function (err, data) {
      if (err) {
        res.writeHead(500);
        return res.end("Error loading " + url);
      }

      res.writeHead(200);
      res.write(data);
      res.end();
    });
}

/**
 * Called when a client connection is established
 *
 * @event connection
 * @param socket
 */
io.sockets.on("connection", function (socket) {
  var timenets = [];
  var db;
  console.log("New connection");

  // send list of available timenets
  if (timenets.length === 0) {
    console.log("sending timenets list");
    db = openDb();
    db.serialize(function (err) {
      db.each("select * from timenets", function(err, row) {
        timenets.push({id: row.id, name: row.name});
      });
    });
    db.close(function (err) {
      socket.emit("timenet_list", {timenets: timenets});
    });
  }

  /**
   * Called when a client requests timenet data
   *
   * @event get_data
   * @param data contains the timenet id that is requested
   */
  socket.on("get_data", function (data) {
    var id = data.id;
    var persons = [];
    var relationships = [];
    var annotations = [];

    console.log("Received request for timenet " + id);
    db = openDb();

    db.serialize(function() {
      db.each("select * from person where timenets_id = $id;", { $id: id }, function(err, row) {
        if (err) {
          console.log("Error reading from DB!");
        }

        /**
         * A single person. Also used in client
         *
         * @class Person
         * @for Server
         */
        persons[row.id] = {
          id: row.id,
          name: row.name,
          sex: row.sex,
          dateOfBirth: new Date(row.date_of_birth),
          dateOfDeath: new Date(row.date_of_death),
          doi: 0,
          childRelationships: [],
          conjugalRelationships: [],
          annotations: []
        };
      });

      db.each("select * from annotations where timenets_id = $id;", { $id: id }, function(err, row) {
        if (err) {
          console.log("Error reading from DB!");
        }

        /**
         * Annotation. Also used in client
         *
         * @class Annotation
         * @for Server
         */
        annotations[row.id] = {
          id: row.id,
          personId: row.person_id,
          date: new Date(row.annotation_date),
          title: row.title,
          text: row.text,
        };
      });

      db.each("select * from relationship where timenets_id = $id;", { $id: id }, function(err, row) {
        if (err) {
          console.log("Error reading from DB!");
        }

        var startDate;
        var endDate;
        if (row.relationship_type === 2) { // child
          startDate = new Date(persons[row.person1_id].dateOfBirth);
          endDate = new Date(persons[row.person1_id].dateOfDeath);
        } else {
          startDate = new Date(row.relationship_start_date);
          endDate = new Date(row.relationship_end_date);
        }

        /**
         * Relationship. Also used in client
         *
         * @class Relationship
         * @for Server
         */
        relationships[row.id] = {
          person1Id: row.person1_id,
          person2Id: row.person2_id,
          type: row.relationship_type,
          startDate: startDate,
          endDate: endDate
        };
      });
    });

    /**
     * Close the database and send data to the client afterwards
     *
     * @method db.close
     * @for Server
     */
    db.close(function (err) {
      if (!err) {
        // assign relationships to persons
        persons.forEach(function (p) {
          if (p === null) {
            return;
          }
          relationships.forEach(function (rel, i) {
            if (rel === null) {
              return;
            }
            if (rel.person1Id === p.id || rel.person2Id === p.id) {
              if (rel.type === 1) {
                p.conjugalRelationships.push(i);
              } else if (rel.type === 2) {
                p.childRelationships.push(i);
              }
            }
          });
          annotations.forEach(function(anno,i){
            if (anno === null) {
              return;
            }
            if(anno.personId === p.id){
              p.annotations.push(i);
            }

          });


        });

        console.log("Sending data");
        // send the data to the client
        socket.emit("db_data", {persons: persons, relationships: relationships, annotations: annotations});
      }
    });

  });
});
