from flask import Flask, request, jsonify
from context.mcp_bus import MCPBus
from context.mcp_message import MCPMessage
from agents.perception_agent import PerceptionAgent
from agents.planning_agent import PlanningAgent
from agents.control_agent import ControlAgent

app = Flask(__name__)

# Initialize system
bus = MCPBus()
bus.register_agent(PerceptionAgent())
bus.register_agent(PlanningAgent())
bus.register_agent(ControlAgent())

@app.route('/control-system', methods=['POST'])
def process_image():
    try:
        # Get image data from request multipart/form-data as form or files or json
        if request.is_json:
            data = request.get_json()
            data = data['image'] if 'image' in data else None
        elif request.files:
            data = request.files.get('image')
            data = data.read()
        else:
            data = request.form.get('image')
        # validate data
        if not data:
            return jsonify({'error': 'No image data provided'}), 400
        
        input_image = data

        print(input_image, "\n\n")
        
        # Create and send initial message
        msg = MCPMessage(source="Sensor", target="Perception", content=input_image)

        # Process the message through the system
        response = bus.send(msg)
        results = []
        
        while response and response.target:
            results.append({
                'source': response.source,
                'target': response.target,
                'content': response.content
            })
            response = bus.send(response)
            
        if response:
            results.append({
                'source': response.source,
                'target': response.target,
                'content': response.content
            })
            
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
### error handling
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Rate Limit Exceeded'}), 429


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


