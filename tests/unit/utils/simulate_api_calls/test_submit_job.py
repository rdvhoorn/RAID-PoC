from utils.simulate_api_call.submit_job import submit_job

def test_submit_job_success(mocker):
    # Arrange: define a fake successful response, like the API would respond
    mock_response = mocker.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"message": "Created and submitted job with ID 123."}
    mock_response.raise_for_status.return_value = None

    # Patch the actual HTTP call
    # Intuition: if `utils.tasks.submit_job.requests.post` is called, return mock_response (instead of actually calling the function)
    mock_post = mocker.patch("utils.tasks.submit_job.requests.post", return_value=mock_response)

    # Act: call the function we want to test
    result = submit_job("WSI_001", "cellvit")

    # Assert: verify behavior
    # With the mocker, we can assert how often the function was called, and with which parameters
    mock_post.assert_called_once_with(
        "http://localhost:8000/run_job",
        json={"wsi_id": "WSI_001", "tool_name": "cellvit"}
    )
    # With the result of the function, we can assert the output is correct
    assert result == {"message": "Created and submitted job with ID 123."}
