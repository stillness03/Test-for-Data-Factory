from datetime import date
from app.models.credits import Credits
from app.models.payments import Payments
from app.models.plans import Plans
from app.models.dictionary import Dictionary
from decimal import Decimal

def test_get_user_credits_overdue_logic(client, db_session):

    overdue_credit = Credits(
        user_id=1,
        issuance_date=date(2021, 12, 1),
        return_date=date(2021, 12, 20),
        body=Decimal("1000.00"),
        percent=Decimal("200.00"),
        actual_return_date=None
    )

    closed_credit = Credits(
        user_id=1,
        issuance_date=date(2021, 1, 1),
        return_date=date(2021, 1, 15),
        body=Decimal("500.00"),
        percent=Decimal("50.00"),
        actual_return_date=date(2021, 1, 14)
    )

    db_session.add_all([overdue_credit, closed_credit])
    db_session.commit()

    payment = Payments(
        credit_id=closed_credit.id,
        payment_date=date(2021, 1, 14),
        type_id=1,
        sum=Decimal("550.00")
    )

    db_session.add(payment)
    db_session.commit()

    response = client.get("/user_credits/1")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2


def test_get_plans_performance(client, db_session):

    db_session.add_all([
        Dictionary(id=3, name="issuance"),
        Dictionary(id=4, name="payment"),
    ])

    plan = Plans(
        period=date(2021, 5, 1),
        category_id=3,
        sum=Decimal("10000.00")
    )

    credit = Credits(
        user_id=2,
        issuance_date=date(2021, 5, 10),
        body=Decimal("8000.00"),
        percent=0,
        return_date=date(2021, 6, 10)
    )

    db_session.add_all([plan, credit])
    db_session.commit()

    response = client.get("/plans_performance?date=2021-05-31")

    assert response.status_code == 200
    data = response.json()

    assert len(data) > 0
    assert data[0]["performance_percentage"] == "80.0%"



def test_get_yearly_report(client, db_session):
    db_session.add_all([
        Dictionary(id=3, name="issuance"),
        Dictionary(id=4, name="payment"),
    ])

    db_session.add_all([
        Plans(period=date(2021, 1, 1), category_id=3, sum=Decimal("1000")),
        Plans(period=date(2021, 2, 1), category_id=3, sum=Decimal("2000")),
    ])

    c1 = Credits(
        user_id=3,
        issuance_date=date(2021, 1, 1),
        body=Decimal("1000"),
        percent=0,
        return_date=date(2021, 2, 1)
    )

    c2 = Credits(
        user_id=3,
        issuance_date=date(2021, 2, 1),
        body=Decimal("2000"),
        percent=0,
        return_date=date(2021, 3, 1)
    )

    db_session.add_all([c1, c2])
    db_session.commit()

    db_session.add_all([
        Payments(
            credit_id=c1.id,
            payment_date=date(2021, 1, 15),
            sum=Decimal("1000"),
            type_id=1
        ),
        Payments(
            credit_id=c2.id,
            payment_date=date(2021, 2, 15),
            sum=Decimal("2000"),
            type_id=1
        )
    ])

    db_session.commit()

    response = client.get("/yearly_performance/2021")

    assert response.status_code == 200
    data = response.json()

    months = [item["month"] for item in data]

    assert "2021-01" in months
    assert "2021-02" in months


def test_get_user_credits_not_found(client):
    response = client.get("/user_credits/999999")
    assert response.status_code == 200
    assert response.json() == []


def test_get_plans_performance_invalid_date(client):
    response = client.get("/plans_performance?date=31-12-2021")

    assert response.status_code == 400
    assert response.json()["detail"] == "Format must be YYYY-MM-DD"


def test_get_plans_performance_zero_plan(client, db_session):
    db_session.add(Dictionary(id=5, name="empty_plan"))
    db_session.add(Plans(period=date(2021, 1, 1), category_id=5, sum=Decimal("0.00")))
    db_session.commit()

    response = client.get("/plans_performance?date=2021-01-01")
    assert response.status_code == 200
    data = response.json()

    assert data[0]["performance_percentage"] == "0.0%"


def test_get_yearly_report_empty_year(client):
    response = client.get("/yearly_performance/1900")
    assert response.status_code == 200
    assert response.json() == []


def test_get_plans_performance_zero_sum(client, db_session):
    db_session.add(Dictionary(id=99, name="zero_cat"))
    db_session.add(Plans(period=date(2021, 1, 1), category_id=99, sum=Decimal("0.00")))
    db_session.commit()

    response = client.get("/plans_performance?date=2021-01-01")

    assert response.status_code == 200
    data = response.json()
    zero_plan = next(item for item in data if item["category"] == "zero_cat")
    assert zero_plan["performance_percentage"] == "0.0%"


def test_get_user_credits_empty_user(client):
    response = client.get("/user_credits/99999")
    assert response.status_code == 200
    assert response.json() == []