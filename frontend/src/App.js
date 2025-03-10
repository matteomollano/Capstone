import React, { useState, useEffect } from 'react'

function App() {
  const [data, setData] = useState([{}]);

  useEffect(() => {
    fetch("/home").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div>

      {(typeof data.packets === 'undefined') ? (
        <p>Loading...</p>
      ) : (
        data.packets.map((packet, i) => (
          <p key={i}>{packet}</p>
        ))
      )}

    </div>
  )
}

export default App