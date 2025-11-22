import React, {
  useEffect,
  useRef,
  forwardRef,
  useImperativeHandle,
  useState,
} from "react";

const Terminal = forwardRef(({ wsUrl }, ref) => {
  const [lines, setLines] = useState([]);
  const wsRef = useRef(null);

  useImperativeHandle(ref, () => ({
    runCmd: (cmdKey) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ cmd: cmdKey }));
      } else {
        connectAndSend(cmdKey);
      }
    },
    clear: () => setLines([]),
  }));

  const addLine = (l) => {
    setLines((prev) => [...prev, l]);
    const el = document.getElementById("terminal-scroll");
    if (el) setTimeout(() => (el.scrollTop = el.scrollHeight), 10);
  };

  const connectAndSend = (cmdKey) => {
    console.log("Connecting to WebSocket:", wsUrl);
    console.log("Command:", cmdKey);
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log("WebSocket connected, sending command:", cmdKey);
      addLine(`> Running ${cmdKey} ...`);
      wsRef.current.send(JSON.stringify({ cmd: cmdKey }));
    };
    
    wsRef.current.onmessage = (ev) => {
      console.log("WebSocket message received:", ev.data);
      addLine(ev.data);
    };
    
    wsRef.current.onerror = (err) => {
      console.error("WebSocket error:", err);
      addLine("> Error connecting to backend");
    };
    
    wsRef.current.onclose = () => {
      console.log("WebSocket closed");
      addLine("> Connection closed.");
    };
  };

  useEffect(() => () => wsRef.current?.close(), []);

  return (
    <div
      style={{
        background: "#0f172a",
        color: "#d1d5db",
        fontFamily: "monospace",
        padding: "12px",
        borderRadius: "8px",
        height: "360px",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <div
        id="terminal-scroll"
        style={{
          flex: 1,
          overflowY: "auto",
          whiteSpace: "pre-wrap",
          paddingRight: "6px",
        }}
      >
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </div>
  );
});

export default Terminal;
