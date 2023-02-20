import requests
import sqlite3
import csv
import pandas as pd

class Pokemon:
    def __init__(self, name, image, abilities, stats, types):
        self.name = name
        self.image = image
        self.abilities = abilities
        self.stats = stats
        self.types = types
    
    def __str__(self):
        abilities_str = ", ".join(self.abilities)
        stats_str = ", ".join(f"{stat}: {value}" for stat, value in self.stats.items())
        types_str = ", ".join(self.types)
        return f"Nombre: {self.name}\nImagen: {self.image}\nHabilidades: {abilities_str}\nEstadísticas: {stats_str}\nTipo: {types_str}"
    

url = "https://pokeapi.co/api/v2/pokemon"
response = requests.get(url)
pokemon_data = response.json()

# Crear una lista de objetos Pokemon a partir de los datos obtenidos de la API
pokemon_list = []
for pokemon in pokemon_data['results']:
    pokemon_url = pokemon['url']
    pokemon_response = requests.get(pokemon_url)
    pokemon_info = pokemon_response.json()
    
    name = pokemon_info['name']
    image = pokemon_info['sprites']['front_default']
    abilities = [ability['ability']['name'] for ability in pokemon_info['abilities']]
    stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_info['stats']}
    types = [pokemon_type['type']['name'] for pokemon_type in pokemon_info['types']]
    
    pokemon_obj = Pokemon(name, image, abilities, stats, types)
    pokemon_list.append(pokemon_obj)

# consultar datos del pokemon po rposicion
print(pokemon_list[0])

# Conectar a la base de datos
conn = sqlite3.connect("pokemon.db")
cursor = conn.cursor()

# Insertar los datos en la tabla
for pokemon in pokemon_list:
    cursor.execute("INSERT INTO pokemon (name, image, abilities, stats, types) VALUES (?, ?, ?, ?, ?)",
                   (pokemon.name, pokemon.image, ",".join(pokemon.abilities), str(pokemon.stats), ",".join(pokemon.types)))

# Guardar los cambios en la base de datos
conn.commit()

# Consultar los pokemones con más de dos tipos
cursor.execute("SELECT name, types FROM pokemon WHERE (LENGTH(types) - LENGTH(REPLACE(types, ',', ''))) >= 1;") 
rows = cursor.fetchall()        # en la api los datos que se obtienen no hgay pokemones con con mas de 2 tipos
                                # igual en la consulta con solo cambiar el valor 1 < #, obtienes 2 o mas tipos

# Guardar los resultados en un archivo CSV
with open("pokemons_multi_types.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "types"])
    writer.writerows(rows)

# Consultar el tipo más común
cursor.execute("WITH temp (var) AS ( SELECT substr(types, 1, instr(types, ',') - 1) FROM pokemon UNION ALL SELECT substr(types, instr(types, ',') + 1) FROM pokemon) SELECT var, COUNT(var) AS frequency FROM temp GROUP BY var HAVING var IS NOT NULL AND var != '' ORDER BY frequency DESC LIMIT 1;")
row = cursor.fetchone()

# Guardar el resultado en un archivo CSV
with open("most_common_type.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["types", "type_count"])
    writer.writerow(row)

# Cerrar la conexión a la base de datos
conn.close()

df1 = pd.read_csv("pokemons_multi_types.csv")
df2 = pd.read_csv("most_common_type.csv")

result = pd.concat([df1, df2], axis=0, ignore_index=True)

result.to_csv("result.csv", index=False)


# SQL

# #Consultar el tipo más común
# WITH temp (var) AS (
#   SELECT substr(types, 1, instr(types, ',') - 1)
#   FROM pokemon
#   UNION ALL
#   SELECT substr(types, instr(types, ',') + 1)
#   FROM pokemon
# )
# SELECT var, COUNT(var) AS frequency
# FROM temp
# GROUP BY var
# HAVING var IS NOT NULL AND var != ''
# ORDER BY frequency DESC
# LIMIT 4;

# #Consultar los pokemones con más de dos tipos
# SELECT name, types
# FROM pokemon
# WHERE (LENGTH(types) - LENGTH(REPLACE(types, ',', ''))) >= 1;